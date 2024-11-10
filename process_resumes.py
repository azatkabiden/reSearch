import os
import re
import json
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
import docx
import chardet
import spacy
from collections import Counter
from nltk.corpus import stopwords
import nltk
import pymorphy2
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    NamesExtractor,
    DatesExtractor,
    Doc
)
from datetime import datetime

# Инициализация инструментов
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('russian'))
nlp = spacy.load("ru_core_news_lg")
morph = pymorphy2.MorphAnalyzer()

# Инициализация компонентов Natasha
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)

# Настройка логирования
logging.basicConfig(
    filename='logs/processing.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функции для обработки изображений и извлечения текста из PDF, DOCX, TXT
def deskew_image(image):
    coords = np.column_stack(np.where(image > 0))
    if len(coords) == 0:
        return image  # Возвращаем оригинальное изображение, если нет текста
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def remove_shadows_and_noise(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)
    shadow = cv2.subtract(image, opening)
    _, thresh = cv2.threshold(shadow, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    result = cv2.bitwise_not(thresh)
    return result

def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(image)
    return enhanced

def scale_image(image, scale_factor=2.0):
    height, width = image.shape[:2]
    new_dimensions = (int(width * scale_factor), int(height * scale_factor))
    scaled = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_CUBIC)
    return scaled

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Извлечение блоков текста с координатами
            blocks = page.get_text("blocks")
            # Сортировка блоков по координатам (сначала сверху вниз, затем слева направо)
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
            
            for block in blocks:
                block_text = block[4].strip()
                if block_text:
                    text += block_text + '\n'
            
            # Извлечение изображений и применение OCR
            image_list = page.get_images(full=True)
            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image['image']
                
                # Чтение изображения из байтов в память
                image = np.frombuffer(image_bytes, dtype=np.uint8)
                img = cv2.imdecode(image, cv2.IMREAD_COLOR)
                
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    gray = deskew_image(gray)
                    gray = remove_shadows_and_noise(gray)
                    gray = enhance_contrast(gray)
                    gray = scale_image(gray, scale_factor=2.0)
                    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                    
                    # Настройки для Tesseract
                    custom_config = r'--oem 3 --psm 6'
                    ocr_result = pytesseract.image_to_string(gray, lang='rus+eng', config=custom_config)
                    
                    text += ocr_result + '\n'
        
        logging.info(f"Успешно обработан PDF: {os.path.basename(pdf_path)}")
        return (os.path.basename(pdf_path), text)
    
    except Exception as e:
        logging.error(f"Ошибка при обработке PDF {os.path.basename(pdf_path)}: {e}")
        return (os.path.basename(pdf_path), f"Ошибка при обработке PDF: {e}")

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        logging.info(f"Успешно обработан DOCX: {os.path.basename(docx_path)}")
        return (os.path.basename(docx_path), text)
    except Exception as e:
        logging.error(f"Ошибка при обработке DOCX {os.path.basename(docx_path)}: {e}")
        return (os.path.basename(docx_path), f"Ошибка при обработке DOCX: {e}")

def extract_text_from_txt(txt_path):
    try:
        # Определение кодировки файла
        with open(txt_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        with open(txt_path, 'r', encoding=encoding if encoding else 'utf-8', errors='ignore') as f:
            text = f.read()
        
        logging.info(f"Успешно обработан TXT: {os.path.basename(txt_path)}")
        return (os.path.basename(txt_path), text)
    except Exception as e:
        logging.error(f"Ошибка при обработке TXT {os.path.basename(txt_path)}: {e}")
        return (os.path.basename(txt_path), f"Ошибка при обработке TXT: {e}")

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        logging.warning(f"Неподдерживаемый формат файла: {file_path}")
        return (os.path.basename(file_path), "Неподдерживаемый формат файла")

def process_files_in_folder(folder_path, max_workers=4):
    # Проверка существования папки
    if not os.path.isdir(folder_path):
        logging.error(f"Папка не найдена: {folder_path}")
        return []
    
    # Собираем список всех поддерживаемых файлов
    supported_extensions = ['.pdf', '.docx', '.txt']
    files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if os.path.splitext(file)[1].lower() in supported_extensions
    ]
    
    if not files:
        logging.warning(f"В папке не найдено поддерживаемых файлов: {folder_path}")
        return []
    
    results = []
    
    # Используем ThreadPoolExecutor для параллельной обработки
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(extract_text, file): file for file in files}
        
        # Используем tqdm для отображения прогресса
        for future in tqdm(as_completed(future_to_file), total=len(future_to_file), desc="Обработка файлов"):
            file = future_to_file[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logging.error(f"Ошибка при обработке {os.path.basename(file)}: {exc}")
                results.append((os.path.basename(file), f"Ошибка при обработке файла: {exc}"))
    
    return results

# Укажите путь к папке с резюме
input_folder = os.path.join(os.path.dirname(__file__), 'uploads')  # Путь к папке с загруженными резюме

# Обрабатываем все поддерживаемые файлы в папке
extracted_texts = process_files_in_folder(input_folder, max_workers=8)

# Путь для сохранения извлеченного текста
extracted_output_folder = os.path.join(os.path.dirname(__file__), 'extracted_texts')

# Создаем папку, если ее нет
os.makedirs(extracted_output_folder, exist_ok=True)

for filename, text in extracted_texts:
    # Проверяем, содержит ли текст ошибку
    if text.startswith("Ошибка при обработке") or text == "Неподдерживаемый формат файла":
        logging.warning(f"Пропуск сохранения для {filename} из-за ошибки обработки или неподдерживаемого формата.")
        continue
    
    # Формируем имя текстового файла
    text_filename = os.path.splitext(filename)[0] + '.txt'
    text_path = os.path.join(extracted_output_folder, text_filename)
    
    # Сохраняем текст
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)

# Теперь приступаем к обработке извлеченных текстов из папки 'extracted_texts'

# Путь к папке с извлеченными текстами
text_input_folder = extracted_output_folder
output_folder = os.path.join(os.path.dirname(__file__), 'data', 'candidates')

# Создание папки для JSON, если ее нет
os.makedirs(output_folder, exist_ok=True)

# Получение списка всех .txt файлов в text_input_folder
txt_files = [f for f in os.listdir(text_input_folder) if f.lower().endswith('.txt')]

# Проверка наличия файлов
if not txt_files:
    logging.warning(f"В папке {text_input_folder} не найдено файлов с расширением .txt.")
    print(f"В папке {text_input_folder} не найдено файлов с расширением .txt.")
else:
    print(f"Найдено {len(txt_files)} файлов для обработки.")

# Функции для обработки текста резюме и извлечения структурированных данных
def clean_text(text):
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+\n', '\n', text)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_name(text):
    first_lines = '\n'.join(text.split('\n')[:5])
    doc = Doc(first_lines)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.tag_ner(ner_tagger)
    for span in doc.spans:
        span.normalize(morph_vocab)
    for span in doc.spans:
        if span.type == 'PER':
            return span.normal
    # Если не нашли с помощью NER, используем NamesExtractor напрямую
    matches = names_extractor(first_lines)
    for match in matches:
        name = match.fact
        full_name = ' '.join(filter(None, [name.first, name.middle, name.last]))
        return full_name
    # Альтернативный способ с использованием регулярных выражений
    name_match = re.search(r'^([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)', first_lines)
    if name_match:
        return name_match.group(1)
    return ""

def extract_contact_info(text):
    contact_info = {}
    # Телефон
    phone_match = re.findall(r'(\+?\d[\d\-\s]{7,}\d)', text)
    contact_info['Телефон'] = phone_match[0] if phone_match else ""
    # Email
    email_match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    contact_info['Email'] = email_match[0] if email_match else ""
    return contact_info

def extract_gender(text):
    gender_match = re.search(r'\b(Мужчина|Женщина)\b', text, re.IGNORECASE)
    if gender_match:
        return gender_match.group(1).capitalize()
    # Попробуем определить пол по имени
    name = extract_name(text)
    if name:
        first_name = name.split()[0]
        parsed_names = morph.parse(first_name)
        for parsed_name in parsed_names:
            gender = parsed_name.tag.gender
            if gender is not None:
                if 'masc' in gender:
                    return 'Мужчина'
                elif 'femn' in gender:
                    return 'Женщина'
    return ""

def parse_date(date_str):
    month_map = {
        'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4, 'май': 5, 'июнь':6,
        'июль':7, 'август':8, 'сентябрь':9, 'октябрь':10, 'ноябрь':11, 'декабрь':12,
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня':6,
        'июля':7, 'августа':8, 'сентября':9, 'октября':10, 'ноября':11, 'декабря':12
    }
    if date_str.strip().lower() in ['настоящее время', 'по настоящее время']:
        return datetime.now()
    parts = date_str.strip().lower().split()
    if len(parts) == 2:
        month = month_map.get(parts[0])
        year = int(parts[1])
        if month:
            return datetime(year, month, 1)
    elif len(parts) == 1:
        # Возможно, указан только год
        year = int(parts[0])
        return datetime(year, 1, 1)
    raise ValueError('Invalid date format')

def extract_experience_years(text):
    dates = re.findall(r'(\w+\s+\d{4}|\d{4})\s*[—\-–]\s*(\w+\s+\d{4}|настоящее время|\d{4})', text.lower())
    total_months = 0
    for start_str, end_str in dates:
        try:
            start_date = parse_date(start_str)
            end_date = parse_date(end_str)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
        except Exception as e:
            continue
    if total_months > 0:
        years = total_months // 12
        return str(years)
    return ""

def extract_education_category(text):
    education_section = re.search(r'(Образование.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if education_section:
        education_text = education_section.group(1)
        if re.search(r'Магистр|Магистратура', education_text, re.IGNORECASE):
            return "Магистр"
        elif re.search(r'Бакалавр|Бакалавриат', education_text, re.IGNORECASE):
            return "Бакалавр"
        elif re.search(r'Доктор|Аспирантура', education_text, re.IGNORECASE):
            return "Доктор"
        elif re.search(r'Высшее', education_text, re.IGNORECASE):
            return "Высшее"
        elif re.search(r'Среднее профессиональное', education_text, re.IGNORECASE):
            return "Среднее профессиональное"
    return ""

def extract_languages(text):
    languages_section = re.search(r'(Владение языками|Знание языков|Языки)\s*[:\-]?\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if languages_section:
        languages_text = languages_section.group(2)
        languages_text = languages_text.strip()
        languages_text = re.sub(r'\s+', ' ', languages_text)
        return languages_text
    return ""

def extract_last_position(text):
    experience_sections = re.split(r'(Опыт работы|Профессиональный опыт)', text, flags=re.IGNORECASE)
    if len(experience_sections) > 1:
        experience_text = experience_sections[-1]
        # Ищем первую запись опыта работы
        position_match = re.search(r'(?:\w+\s+\d{4}|\d{4})\s*[—\-–]\s*(?:\w+\s+\d{4}|настоящее время|\d{4})\s*(.*?)\n', experience_text)
        if position_match:
            return position_match.group(1).strip()
    return ""

def extract_skills(text):
    skills = {'Soft Skills': '', 'Hard Skills': ''}
    skills_section = re.search(r'(Ключевые навыки|Навыки|Профессиональные навыки)\s*[:\-]?\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        skills_text = skills_section.group(2)
        skills_text = skills_text.strip()
        skills_text = re.sub(r'\s+', ' ', skills_text)
        skills_list = [skill.strip() for skill in re.split(r',|;', skills_text) if skill.strip()]
        # Разделение на Soft и Hard Skills
        soft_skills_keywords = ['коммуникация', 'лидерство', 'организация', 'управление', 'ведение переговоров', 'командная работа', 'обучение', 'ответственность', 'стрессоустойчивость', 'внимательность', 'креативность', 'инициативность', 'дисциплина']
        soft_skills = []
        hard_skills = []
        for skill in skills_list:
            if any(word in skill.lower() for word in soft_skills_keywords):
                soft_skills.append(skill)
            else:
                hard_skills.append(skill)
        skills['Soft Skills'] = ', '.join(soft_skills)
        skills['Hard Skills'] = ', '.join(hard_skills)
    return skills

def extract_certifications(text):
    certifications_section = re.search(r'(Сертификаты|Сертификации|Certificates|Повышение квалификации|Курсы)\s*[:\-]?\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if certifications_section:
        certifications_text = certifications_section.group(2)
        certifications_text = certifications_text.strip()
        certifications_text = re.sub(r'\s+', ' ', certifications_text)
        return certifications_text
    return ""

def extract_personal_qualities(text):
    qualities_section = re.search(r'(Личностные качества|Personal qualities|Обо мне|Дополнительная информация)\s*[:\-]?\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if qualities_section:
        qualities_text = qualities_section.group(2)
        qualities_text = qualities_text.strip()
        qualities_text = re.sub(r'\s+', ' ', qualities_text)
        return qualities_text
    return ""

def extract_summary(text):
    summary_section = re.search(r'(Summary|Обо мне|Кратко о себе|Дополнительная информация|Об обо мне)\s*[:\-]?\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if summary_section:
        summary_text = summary_section.group(2)
        summary_text = summary_text.strip()
        summary_text = re.sub(r'\s+', ' ', summary_text)
        return summary_text
    return ""

def extract_desired_salary(text):
    salary_match = re.search(r'(Заработная плата|Желаемая зарплата|Зарплата|Желаемый доход)\s*[:\-]?\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if salary_match:
        salary = salary_match.group(2).strip()
        return salary
    return ""

def extract_work_schedule(text):
    schedule_match = re.search(r'(График работы|Тип занятости|Занятость)\s*[:\-]?\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if schedule_match:
        schedule = schedule_match.group(2).strip()
        return schedule
    return ""

def extract_field_of_activity(text):
    desired_position_section = re.search(r'Желаемая должность и зарплата\s*(.*?)((\n[A-ZА-Я].*)|$)', text, re.IGNORECASE | re.DOTALL)
    if desired_position_section:
        position_text = desired_position_section.group(1)
        # Извлекаем специализации
        specializations_match = re.search(r'Специализации\s*[:\-]?\s*(.*?)(?:\n|$)', position_text, re.IGNORECASE)
        if specializations_match:
            return specializations_match.group(1).strip()
        else:
            # Берем первую строку после заголовка
            lines = position_text.strip().split('\n')
            if lines:
                return lines[0].strip()
    return ""

def process_resume(resume_text, candidate_id):
    resume_data = {
        "Summary": "",
        "Категория образования": "",
        "Стаж работы (лет)": "", 
        "Пол": "",
        "Направление деятельности": "",
        "Последняя должность": "",
        "Владение языками": "",
        "График работы": "",
        "Заработная плата": "",
        "Личностные качества": "",
        "Soft Skills": "",
        "Hard Skills": "",
        "Сертификации": "",
        "id": candidate_id, 
        "ФИО": ""
    }
    resume_text = clean_text(resume_text)
    
    # Извлечение данных
    resume_data["ФИО"] = extract_name(resume_text)
    contact_info = extract_contact_info(resume_text)
    resume_data["Телефон"] = contact_info.get("Телефон", "")
    resume_data["Email"] = contact_info.get("Email", "")
    resume_data["Пол"] = extract_gender(resume_text)
    resume_data["Стаж работы (лет)"] = extract_experience_years(resume_text)
    resume_data["Категория образования"] = extract_education_category(resume_text)
    resume_data["Владение языками"] = extract_languages(resume_text)
    resume_data["Последняя должность"] = extract_last_position(resume_text)
    skills = extract_skills(resume_text)
    resume_data["Soft Skills"] = skills["Soft Skills"]
    resume_data["Hard Skills"] = skills["Hard Skills"]
    resume_data["Сертификации"] = extract_certifications(resume_text)
    resume_data["Личностные качества"] = extract_personal_qualities(resume_text)
    resume_data["Summary"] = extract_summary(resume_text)
    resume_data["Заработная плата"] = extract_desired_salary(resume_text)
    resume_data["График работы"] = extract_work_schedule(resume_text)
    resume_data["Направление деятельности"] = extract_field_of_activity(resume_text)
    
    # Дополнительная очистка данных
    for key in resume_data:
        if isinstance(resume_data[key], str):
            resume_data[key] = resume_data[key].strip()
            resume_data[key] = re.sub(r'\s+', ' ', resume_data[key])
    return resume_data

# Получаем текущий максимальный ID кандидата
existing_candidate_files = [f for f in os.listdir(output_folder) if f.startswith('candidate') and f.endswith('.json')]
existing_ids = [int(re.findall(r'\d+', f)[0]) for f in existing_candidate_files]
current_max_id = max(existing_ids) if existing_ids else 0

# Основной цикл обработки всех резюме
for idx, txt_file in enumerate(tqdm(txt_files, desc="Обработка резюме"), start=current_max_id + 1):
    file_path = os.path.join(text_input_folder, txt_file)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
    except Exception as e:
        logging.error(f"Ошибка чтения файла {file_path}: {e}")
        continue

    resume_data = process_resume(resume_text, idx)

    # Сохранение в JSON файл
    output_filename = f"candidate{idx}.json"
    output_path = os.path.join(output_folder, output_filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            json.dump(resume_data, out_f, ensure_ascii=False, indent=4)
        logging.info(f"Успешно обработано {file_path} -> {output_filename}")
        print(f"Обработано {output_filename}")
    except Exception as e:
        logging.error(f"Ошибка записи файла {output_filename}: {e}")

print("Обработка завершена.")

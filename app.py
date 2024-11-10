from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, g
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import time  # Импортируем модуль time для измерения времени

app = Flask(__name__)
app.secret_key = 'bonfire.ltd'  # Замените на ваш секретный ключ

# Инициализация модели
print("Инициализация модели...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Модель успешно инициализирована.")

# Функция для загрузки и векторизации резюме
def load_and_vectorize_resumes():
    start_time = time.time()  # Начало отсчёта времени
    print("Загрузка и векторизация резюме...")
    resumes = []
    resume_vectors = []
    candidates_dir = os.path.join(app.root_path, 'data', 'candidates')

    for filename in os.listdir(candidates_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(candidates_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                resume = json.load(f)
                resumes.append(resume)
                # Векторизация резюме
                text = ' '.join([f"{key}: {value}" for key, value in resume.items()])
                resume_vector = model.encode(text)
                resume_vectors.append(resume_vector)
    print(f"Загружено и векторизировано {len(resumes)} резюме.")
    end_time = time.time()  # Конец отсчёта времени
    elapsed_time = end_time - start_time
    print(f"Векторизация резюме заняла {elapsed_time:.2f} секунд.")  # Вывод времени векторации
    return resumes, resume_vectors

# Загрузка резюме и их векторов при запуске приложения
resumes, resume_vectors = load_and_vectorize_resumes()

# Функция для сохранения истории поиска
def save_search_history(query, candidates):
    if 'history' not in session:
        session['history'] = []
    # Сохраняем последние 10 запросов
    session['history'].insert(0, {'query': query, 'candidates': candidates})
    session['history'] = session['history'][:10]
    session.modified = True
    print("История поиска обновлена.")

# Хуки для измерения времени обработки запросов
@app.before_request
def before_request():
    g.start_time = time.time()  # Запоминаем время начала запроса

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed_time = time.time() - g.start_time
        print(f"Время обработки запроса {request.path}: {elapsed_time:.2f} секунд.")
    return response

# Главная страница
@app.route('/')
def landing():
    return render_template('landing.html')

# Страница поиска кандидатов
@app.route('/search', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        print("Получен GET-запрос на /search")
        return render_template('index.html')
    else:
        print("Получен POST-запрос на /search")
        data = request.get_json()
        print("Данные запроса:", data)

        if data is None or 'query' not in data:
            print("Неверный формат данных запроса.")
            abort(400)

        query = data.get('query', '').lower()
        matching_candidates = []

        # Векторизация запроса HR
        prompt_vector = model.encode(query)
        print("Запрос векторизован.")

        # Вычисление косинусного сходства
        similarity_scores = []
        for resume_vector in resume_vectors:
            similarity = np.dot(prompt_vector, resume_vector) / (np.linalg.norm(prompt_vector) * np.linalg.norm(resume_vector))
            similarity_scores.append(similarity)

        # Пороговое значение сходства
        threshold = 0.60  # Установлен порог 60%

        # Поиск подходящих кандидатов
        for i, score in enumerate(similarity_scores):
            if score >= threshold:
                candidate = resumes[i]
                matching_candidates.append({
                    'FИО': candidate.get('ФИО') or "Неизвестный кандидат",
                    'id': str(candidate.get('id')),  # Преобразуем ID в строку
                    'score': round(score * 100, 2)  # Сохраняем процент сходства
                })

        # Сортировка кандидатов по убыванию % совпадения
        matching_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Ограничение количества возвращаемых кандидатов (например, до 20)
        matching_candidates = matching_candidates[:20]

        # Сохраняем историю поиска
        save_search_history(query, matching_candidates)

        print(f"Найдено {len(matching_candidates)} кандидатов.")

        return jsonify({'candidates': matching_candidates})

# Маршрут для отображения истории поиска
@app.route('/history')
def history():
    history = session.get('history', [])
    return render_template('history.html', history=history)

# Маршрут для удаления записи из истории
@app.route('/delete_history', methods=['POST'])
def delete_history():
    index = request.form.get('index', type=int)
    print(f"Запрос на удаление записи из истории: Index = {index}")
    if 'history' in session:
        try:
            session['history'].pop(index)
            session.modified = True
            print(f"Запись с индексом {index} удалена из истории.")
            return jsonify({'status': 'success'})
        except IndexError:
            print("Неверный индекс при удалении из истории.")
            return jsonify({'status': 'error', 'message': 'Invalid index'}), 400
    else:
        print("История поиска не найдена при попытке удаления.")
        return jsonify({'status': 'error', 'message': 'No history found'}), 400

# Маршрут для получения профиля кандидата
@app.route('/profile/<int:candidate_id>')
def profile(candidate_id):
    candidates_dir = os.path.join(app.root_path, 'data', 'candidates')
    filepath = os.path.join(candidates_dir, f'candidate{candidate_id}.json')  # Предполагается, что файл назван как 'candidate{id}.json'

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            candidate = json.load(f)
        return render_template('profile.html', candidate=candidate, candidate_id=str(candidate_id))
    else:
        return "Кандидат не найден", 404

# Маршрут для добавления кандидата в избранное
@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    candidate_id = str(request.form.get('candidate_id'))  # Преобразуем ID в строку
    print(f"Добавление кандидата в избранное: ID = {candidate_id}")
    if 'favorites' not in session:
        session['favorites'] = []
    if candidate_id and candidate_id not in session['favorites']:
        session['favorites'].append(candidate_id)
        session.modified = True
        print(f"Кандидат добавлен в избранное. Текущее избранное: {session['favorites']}")
    else:
        print(f"Кандидат с ID {candidate_id} уже в избранном или ID отсутствует.")
    return jsonify({'status': 'added'})

# Маршрут для удаления кандидата из избранного
@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    candidate_id = str(request.form.get('candidate_id'))  # Преобразуем ID в строку
    print(f"Удаление кандидата из избранного: ID = {candidate_id}")
    if 'favorites' in session and candidate_id in session['favorites']:
        session['favorites'].remove(candidate_id)
        session.modified = True
        print(f"Кандидат удалён из избранного. Текущее избранное: {session['favorites']}")
    else:
        print(f"Кандидат с ID {candidate_id} не найден в избранном.")
    return jsonify({'status': 'removed'})

# Маршрут для отображения избранных кандидатов
@app.route('/favorites')
def favorites():
    favorites = session.get('favorites', [])
    candidates = []
    candidates_dir = os.path.join(app.root_path, 'data', 'candidates')

    for candidate_id in favorites:
        filepath = os.path.join(candidates_dir, f'candidate{candidate_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                candidate = json.load(f)
                candidates.append({
                    'FИО': candidate.get('ФИО') or "Неизвестный кандидат",
                    'id': str(candidate_id)  # Преобразуем ID в строку
                })
        else:
            print(f"Файл кандидата с ID {candidate_id} не найден.")
    
    return render_template('favorites.html', candidates=candidates)

if __name__ == '__main__':
    app.run(debug=True)

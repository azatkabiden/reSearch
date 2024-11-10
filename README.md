# HR Candidate Search Platform

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Landing Page](#1-landing-page)
  - [2. Upload Resume Page (`/upload_resume`)](#2-upload-resume-page-upload_resume)
  - [3. Search Page (`/search`)](#3-search-page-search)
  - [4. Favorites Page (`/favorites`)](#4-favorites-page-favorites)
  - [5. History Page (`/history`)](#5-history-page-history)
  - [6. Candidate Profile Page (`/profile/<candidate_id>`)](#6-candidate-profile-page-profilecandidate_id)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [1. Data Preparation](#1-data-preparation)
  - [2. Resume Processing](#2-resume-processing)
  - [3. Vectorization Process](#3-vectorization-process)
  - [4. Handling User Searches](#4-handling-user-searches)
  - [5. Displaying Results](#5-displaying-results)
  - [6. Favorites and History Management](#6-favorites-and-history-management)
  - [7. Performance Monitoring](#7-performance-monitoring)
- [API Endpoints](#api-endpoints)
  - [1. `/` (Landing Page)](#1--landing-page)
  - [2. `/upload_resume` (Upload Resume Page)](#2-upload_resume-upload-resume-page)
  - [3. `/process_resumes` (Process Resumes)](#3-process_resumes-process-resumes)
  - [4. `/search` (Search Page)](#4-search-search-page)
  - [5. `/history` (History Page)](#5-history-history-page)
  - [6. `/delete_history` (Delete History Entry)](#6-delete_history-delete-history-entry)
  - [7. `/profile/<candidate_id>` (Candidate Profile Page)](#7-profilecandidate_id-candidate-profile-page)
  - [8. `/add_favorite` (Add Candidate to Favorites)](#8-add_favorite-add-candidate-to-favorites)
  - [9. `/remove_favorite` (Remove Candidate from Favorites)](#9-remove_favorite-remove-candidate-from-favorites)
  - [10. `/favorites` (Favorites Page)](#10-favorites-favorites-page)
- [Contributing](#contributing)

## Overview

The HR Candidate Search Platform is a comprehensive web application designed to streamline the recruitment process for HR specialists. Leveraging advanced natural language processing (NLP) and vectorization techniques, the platform enables efficient searching, ranking, and management of candidate profiles based on detailed job descriptions. Users can upload resumes in various formats, automatically extract structured data, and maintain a dynamic candidate database. With features like favorites management and search history, the platform ensures a seamless and productive hiring experience.

## Features

- **Efficient Candidate Search:** Input detailed descriptions of ideal candidates and receive ranked results based on match percentage.
- **Automatic Resume Processing:** Upload resumes in PDF, DOCX, or TXT formats. The system automatically extracts text, processes the content, and adds structured candidate data to the database.
- **Automatic Vectorization:** Utilizes SentenceTransformer to vectorize search queries and candidate resumes for accurate similarity assessments.
- **Detailed Candidate Profiles:** Access comprehensive profiles of candidates, including education, work experience, skills, and certifications.
- **Upload and Process Resumes:** HR specialists can upload new resumes directly through the platform, which are then processed and integrated into the candidate database.
- **Favorites Management:** Add preferred candidates to a favorites list for quick and easy access.
- **Search History:** Maintain a history of past search queries and results for reference and reuse.
- **Pagination:** Navigate through search results efficiently with pagination controls.
- **Responsive Design:** Optimized for various devices, ensuring accessibility on desktops, tablets, and smartphones.
- **User-Friendly Interface:** Intuitive and clean UI built with Bootstrap for enhanced user experience.

## Technology Stack

- **Backend:**
  - [Flask](https://flask.palletsprojects.com/) - A lightweight WSGI web application framework.
  - [SentenceTransformers](https://www.sbert.net/) - For vectorizing text data.
  - [NumPy](https://numpy.org/) - For numerical operations.
  - [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) - For extracting text from PDF files.
  - [pytesseract](https://github.com/madmaze/pytesseract) - For OCR processing of images within PDFs.
  - [OpenCV](https://opencv.org/) - For image processing.
  - [spaCy](https://spacy.io/) - For natural language processing.
  - [Natasha](https://github.com/natasha/natasha) - For advanced NLP in Russian.
  - [pymorphy2](https://github.com/kmike/pymorphy2) - For morphological analysis of the Russian language.
  - [NLTK](https://www.nltk.org/) - For natural language processing tasks.
  - [python-docx](https://python-docx.readthedocs.io/en/latest/) - For reading DOCX files.
  - [tqdm](https://tqdm.github.io/) - For progress bars during processing.
  
- **Frontend:**
  - [Bootstrap 5](https://getbootstrap.com/) - For responsive and modern UI components.
  - [Bootstrap Icons](https://icons.getbootstrap.com/) - For consistent iconography.
  - Custom CSS and JavaScript for enhanced interactivity.

- **Others:**
  - [JSON](https://www.json.org/json-en.html) - For storing candidate profiles.
  - Python's built-in `session` management for handling user data.
  - **Logging:** For tracking processing activities.

## Installation

Follow the steps below to set up and run the HR Candidate Search Platform on your local machine.

### Prerequisites

- **Python 3.7+**: Ensure Python is installed. You can download it from [here](https://www.python.org/downloads/).
- **pip**: Python package manager (usually comes with Python).
- **Virtual Environment (optional but recommended)**: To create an isolated Python environment.
- **Tesseract OCR**: Required for OCR processing of images in resumes.

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/hr-candidate-search.git
   cd hr-candidate-search
   ```

2. **Create and Activate Virtual Environment (Optional)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   **Note:** Ensure that Tesseract OCR is installed on your system.

4. **Install Tesseract OCR**

   - **Windows:**
     - Download and install from [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
     - Add the installation path (e.g., `C:\Program Files\Tesseract-OCR`) to your system's PATH environment variable.

   - **macOS:**

     ```bash
     brew install tesseract
     ```

   - **Linux:**

     ```bash
     sudo apt-get install tesseract-ocr
     ```

5. **Download spaCy Language Model**

   ```bash
   python -m spacy download ru_core_news_lg
   ```

6. **Prepare Candidate Data**

   - Ensure that the `data/candidates/` directory exists.
   - If you have resumes in PDF, DOCX, or TXT formats, you can upload them using the application and process them.
   - Alternatively, you can manually place candidate JSON files in the `data/candidates/` directory.

7. **Run the Application**

   ```bash
   python app.py
   ```

   The application will start in development mode and can be accessed at `http://127.0.0.1:5000/`.

8. **Upload and Process Resumes**

   - Navigate to the "Upload Resume" page (`http://127.0.0.1:5000/upload_resume`).
   - Upload resumes in PDF, DOCX, or TXT formats.
   - Click on "Process Uploaded Resumes" to process them and add candidates to the database.

9. **Accessing the Platform**

   Open your web browser and navigate to `http://127.0.0.1:5000/` to access the HR Candidate Search Platform.

## Usage

### 1. Landing Page

   - **Description:** Provides an overview of the platform's capabilities and directs users to start searching for candidates or upload new resumes.
   - **Action:** Use the navigation menu to access different features like search, upload resumes, favorites, and history.

### 2. Upload Resume Page (`/upload_resume`)

   - **Description:** Allows HR specialists to upload resumes in PDF, DOCX, or TXT formats.
   - **Actions:**
     - **Upload Resumes:** Click "Choose File" to select resume files from your computer and then click "Upload" to upload them to the server.
     - **Process Resumes:** After uploading, click the "Process Uploaded Resumes" button to extract data from the resumes and add new candidates to the database.
     - **Feedback:** The application will display messages indicating the success or failure of each operation.

### 3. Search Page (`/search`)

   - **Input:** Enter a detailed description of the ideal candidate in the provided text area.
   - **Action:** Click the "Find" button to initiate the search.
   - **Process:** The system vectorizes the input description and compares it against the vectorized resumes in the database.
   - **Results:** Displayed in a paginated list, sorted by match percentage. Each candidate entry includes their name, match score, and options to view their profile or add them to favorites.

### 4. Favorites Page (`/favorites`)

   - **Description:** Lists all candidates that have been marked as favorites.
   - **Actions:**
     - **View Profile:** Click on a candidate's name to view their detailed profile.
     - **Remove from Favorites:** Click the "Delete" button to remove a candidate from the favorites list.

### 5. History Page (`/history`)

   - **Description:** Displays a history of past search queries along with the corresponding candidates found.
   - **Actions:**
     - **View Candidates:** Expand a search query to see the list of matching candidates.
     - **Remove from History:** Click the "Delete from History" button to remove a specific search entry.

### 6. Candidate Profile Page (`/profile/<candidate_id>`)

   - **Description:** Shows detailed information about a specific candidate, including education, work experience, skills, and certifications.
   - **Actions:**
     - **Add/Remove Favorite:** Toggle the favorite status of the candidate directly from their profile.
     - **Navigate Back:** Use the navigation menu or browser controls to return to the previous page.

## Project Structure

```
hr-candidate-search/
├── app.py
├── process_resumes.py
├── requirements.txt
├── data/
│   └── candidates/
│       ├── candidate1.json
│       ├── candidate2.json
│       └── ... (other candidate JSON files)
├── uploads/
│   └── ... (uploaded resumes in PDF, DOCX, TXT formats)
├── extracted_texts/
│   └── ... (extracted text from resumes)
├── templates/
│   ├── landing.html
│   ├── index.html
│   ├── upload_resume.html
│   ├── favorites.html
│   ├── history.html
│   ├── profile.html
├── static/
│   ├── css/
│   │   └── custom.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       ├── logo.png
│       └── search-illustration.png
└── README.md
```

- **app.py:** Main Flask application file containing routes and backend logic.
- **process_resumes.py:** Script that processes uploaded resumes, extracting text and structured data.
- **requirements.txt:** Lists all Python dependencies required to run the project.
- **data/candidates/:** Directory containing JSON files for each candidate.
- **uploads/:** Directory where uploaded resumes are stored.
- **extracted_texts/:** Directory containing extracted text files from resumes.
- **logs/:** Directory containing log files for monitoring processing activities.
- **templates/:** HTML templates for different pages of the application.
  - **base.html:** Base template for consistent layout.
  - **landing.html:** Landing page template.
  - **index.html:** Search page template.
  - **upload_resume.html:** Upload resume page template.
  - **favorites.html:** Favorites page template.
  - **history.html:** History page template.
  - **profile.html:** Candidate profile page template.
  - **navbar.html:** Navigation bar included in other templates.
  - **footer.html:** Footer included in other templates.
- **static/:** Contains static assets like CSS, JavaScript, and images.
  - **css/custom.css:** Custom styles for the application.
  - **js/script.js:** JavaScript for handling frontend interactions.
  - **images/:** Directory for storing images used in the application.

## How It Works

### 1. Data Preparation

   - **Candidate Resumes:** HR specialists can upload resumes in PDF, DOCX, or TXT formats via the application. The resumes are stored in the `uploads/` directory.

### 2. Resume Processing

   - **Extraction of Text:** The `process_resumes.py` script processes the uploaded resumes, extracting text using appropriate libraries:
     - **PDFs:** Processed with PyMuPDF (`fitz`) and `pytesseract` for OCR on images.
     - **DOCX:** Processed with `python-docx`.
     - **TXT:** Read directly, with encoding detection via `chardet`.
   - **Text Cleaning and Preparation:** The extracted text is cleaned to remove unnecessary whitespace and formatting inconsistencies.
   - **Data Extraction:** Structured information such as name, contact details, work experience, skills, and other relevant data are extracted using NLP techniques with `Natasha`, `spaCy`, and `pymorphy2`.
   - **Data Storage:** The extracted data is saved as JSON files in the `data/candidates/` directory, each with a unique candidate ID.

### 3. Vectorization Process

   - **Resume Vectorization:** When the application starts or after new resumes are processed, it loads and vectorizes the candidate data from the JSON files.
   - **Incremental Updates:** The application updates the vectorized data to include new candidates without reprocessing existing ones.

### 4. Handling User Searches

   - **Input Processing:** When an HR specialist inputs a job description and initiates a search, the input text is vectorized using the same `SentenceTransformer` model.
   - **Similarity Calculation:** The vectorized query is compared against all stored resume vectors using cosine similarity to determine how well each candidate matches the job description.
   - **Threshold Filtering:** Candidates with a similarity score below a predefined threshold (e.g., 60%) are excluded from the results.
   - **Ranking and Limiting:** The remaining candidates are sorted in descending order based on their similarity scores and limited to a maximum number of results (e.g., 20).

### 5. Displaying Results

   - **Pagination:** Search results are displayed in a paginated format, showing a limited number of candidates per page to enhance readability and navigation.
   - **Candidate Details:** Each candidate entry includes their name, match percentage, and options to view their profile or add them to favorites.
   - **Interactive Elements:** Users can interact with candidates directly from the search results.

### 6. Favorites and History Management

   - **Favorites:** Users can mark candidates as favorites, which are stored in the session. The favorites list can be accessed from the dedicated favorites page.
   - **Search History:** Each search query along with its results is saved in the session history, allowing users to revisit past searches. Users can also delete specific entries from their search history.

### 7. Performance Monitoring

   - **Request Timing:** The application logs the time taken to process each user request, aiding in performance optimization and monitoring.
   - **Logging:** The `process_resumes.py` script logs processing activities and errors to `logs/processing.log` for debugging and monitoring.

## API Endpoints

### 1. `/` (Landing Page)

   - **Method:** GET
   - **Description:** Renders the landing page of the application.

### 2. `/upload_resume` (Upload Resume Page)

   - **Methods:** GET, POST
   - **GET:** Renders the upload resume interface.
   - **POST:** Handles the uploading of resume files.

### 3. `/process_resumes` (Process Resumes)

   - **Method:** GET
   - **Description:** Initiates the processing of uploaded resumes, extracting data and adding candidates to the database.

### 4. `/search` (Search Page)

   - **Methods:** GET, POST
   - **GET:** Renders the search interface.
   - **POST:** Accepts a JSON payload with the search query, processes the search, and returns a JSON response with matching candidates.

   **Request Payload:**

   ```json
   {
       "query": "Your job description here..."
   }
   ```

   **Response:**

   ```json
   {
       "candidates": [
           {
               "FИО": "Иванов Иван Иванович",
               "id": "1",
               "score": 75.34
           },
           ...
       ]
   }
   ```

### 5. `/history` (History Page)

   - **Method:** GET
   - **Description:** Displays the history of past search queries and their results.

### 6. `/delete_history` (Delete History Entry)

   - **Method:** POST
   - **Description:** Deletes a specific search entry from the history based on its index.

   **Request Parameters:**

   - `index` (integer): The index of the history entry to delete.

   **Response:**

   ```json
   {
       "status": "success"
   }
   ```

   or

   ```json
   {
       "status": "error",
       "message": "Invalid index"
   }
   ```

### 7. `/profile/<candidate_id>` (Candidate Profile Page)

   - **Method:** GET
   - **Description:** Displays detailed information about a specific candidate.

### 8. `/add_favorite` (Add Candidate to Favorites)

   - **Method:** POST
   - **Description:** Adds a candidate to the favorites list.

   **Request Parameters:**

   - `candidate_id` (string): The ID of the candidate to add.

   **Response:**

   ```json
   {
       "status": "added"
   }
   ```

### 9. `/remove_favorite` (Remove Candidate from Favorites)

   - **Method:** POST
   - **Description:** Removes a candidate from the favorites list.

   **Request Parameters:**

   - `candidate_id` (string): The ID of the candidate to remove.

   **Response:**

   ```json
   {
       "status": "removed"
   }
   ```

### 10. `/favorites` (Favorites Page)

   - **Method:** GET
   - **Description:** Displays the list of favorite candidates.

## Contributing

We welcome contributions to enhance the HR Candidate Search Platform! Whether it's reporting bugs, suggesting features, or contributing code, your input is valuable.

### Steps to Contribute

1. **Fork the Repository**

   Click the "Fork" button at the top right of the repository page to create a personal copy.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/hr-candidate-search.git
   cd hr-candidate-search
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes**

   Implement your desired features or fixes.

5. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request**

   Navigate to the original repository and click "Compare & pull request" to submit your changes for review.

### Guidelines

- **Code Quality:** Ensure your code follows the project's coding standards and is well-documented.
- **Testing:** Write tests for new features or fixes to maintain code reliability.
- **Issue Reporting:** Before submitting a feature or bug fix, check if the issue has already been reported. If not, open a new issue with detailed information.

---

© 2024 BONFIRE TEAM. All rights reserved.

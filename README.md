# HR Candidate Search Platform

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

## Overview

The HR Candidate Search Platform is a modern web application designed to streamline the recruitment process for HR specialists. By leveraging advanced natural language processing and vectorization techniques, the platform enables efficient searching, ranking, and management of candidate profiles based on detailed job descriptions. Users can effortlessly find the most suitable candidates, maintain a history of search queries, and manage a list of favorite profiles, ensuring a seamless and productive hiring experience.

## Features

- **Efficient Candidate Search:** Input detailed descriptions of ideal candidates and receive ranked results based on match percentage.
- **Automatic Vectorization:** Utilizes SentenceTransformer to vectorize search queries and candidate resumes for accurate similarity assessments.
- **Detailed Candidate Profiles:** Access comprehensive profiles of candidates, including education, work experience, skills, and certifications.
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
  
- **Frontend:**
  - [Bootstrap 5](https://getbootstrap.com/) - For responsive and modern UI components.
  - [Bootstrap Icons](https://icons.getbootstrap.com/) - For consistent iconography.
  - Custom CSS and JavaScript for enhanced interactivity.

- **Others:**
  - [JSON](https://www.json.org/json-en.html) - For storing candidate profiles.
  - Python's built-in `session` management for handling user data.

## Installation

Follow the steps below to set up and run the HR Candidate Search Platform on your local machine.

### Prerequisites

- **Python 3.7+**: Ensure Python is installed. You can download it from [here](https://www.python.org/downloads/).
- **pip**: Python package manager (usually comes with Python).
- **Virtual Environment (optional but recommended)**: To create an isolated Python environment.

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

   *If `requirements.txt` is not present, install the necessary packages manually:*

   ```bash
   pip install Flask sentence-transformers numpy
   ```

4. **Prepare Candidate Data**

   Ensure that the `data/candidates/` directory contains JSON files for each candidate, named in the format `candidate{id}.json` (e.g., `candidate1.json`, `candidate2.json`, etc.).
   If your resumes are in PDF, DOCX, or TXT format, first process them using NLP library with machine learning and deep learning techniques (in our case, it is spaCy, ru_core_news_lg model).

   **Example `candidate1.json`:**

   ```json
   {
       "id": 1,
       "ФИО": "Иванов Иван Иванович",
       "Категория образования": "Высшее",
       "Стаж работы (лет)": 5,
       "Pol": "Мужской",
       "Направление деятельности": "Программирование",
       "Последняя должность": "Senior Developer",
       "Владение языками": "Python, JavaScript, SQL",
       "График работы": "Полный день",
       "Заработная плата": "120000 руб.",
       "Личностные качества": "Ответственность, Коммуникабельность, Стрессоустойчивость",
       "Soft Skills": "Командная работа, Тайм-менеджмент",
       "Hard Skills": "Python, Django, React",
       "Сертификации": "OCJP, AWS Certified Developer"
   }
   ```

6. **Run the Application**

   ```bash
   python app.py
   ```

   The application will start in development mode and can be accessed at `http://127.0.0.1:5000/`.

7. **Accessing the Platform**

   Open your web browser and navigate to `http://127.0.0.1:5000/` to access the HR Candidate Search Platform.

## Usage

### 1. **Landing Page**

   - **Description:** Provides an overview of the platform's capabilities and directs users to start searching for candidates.
   - **Action:** Click the "Start" button to navigate to the search page.

### 2. **Search Page (`/search`)**

   - **Input:** Enter a detailed description of the ideal candidate in the provided text area.
   - **Action:** Click the "Find" button to initiate the search.
   - **Process:** The system vectorizes the input description and compares it against the vectorized resumes in the database.
   - **Results:** Displayed in a paginated list, sorted by match percentage. Each candidate entry includes their name, match score, and an option to add to favorites.

### 3. **Favorites Page (`/favorites`)**

   - **Description:** Lists all candidates that have been marked as favorites.
   - **Actions:**
     - **View Profile:** Click on a candidate's name to view their detailed profile.
     - **Remove from Favorites:** Click the "Delete" button to remove a candidate from the favorites list.

### 4. **History Page (`/history`)**

   - **Description:** Displays a history of past search queries along with the corresponding candidates found.
   - **Actions:**
     - **View Candidates:** Expand a search query to see the list of matching candidates.
     - **Remove from History:** Click the "Delete from History" button to remove a specific search entry.

### 5. **Candidate Profile Page (`/profile/<candidate_id>`)**

   - **Description:** Shows detailed information about a specific candidate, including education, work experience, skills, and certifications.
   - **Actions:**
     - **Add/Remove Favorite:** Toggle the favorite status of the candidate directly from their profile.

## Project Structure

```
hr-candidate-search/
├── app.py
├── requirements.txt
├── data/
│   └── candidates/
│       ├── candidate1.json
│       ├── candidate2.json
│       └── ... (other candidate JSON files)
├── templates/
│   ├── landing.html
│   ├── index.html
│   ├── favorites.html
│   ├── history.html
│   └── profile.html
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
- **requirements.txt:** Lists all Python dependencies required to run the project.
- **data/candidates/:** Directory containing JSON files for each candidate.
- **templates/:** HTML templates for different pages of the application.
- **static/:** Contains static assets like CSS, JavaScript, and images.
  - **css/custom.css:** Custom styles for the application.
  - **js/script.js:** JavaScript for handling frontend interactions.
  - **images/:** Directory for storing images used in the application.

## How It Works

### 1. **Data Preparation**

   - **Candidate Resumes:** Each candidate's resume is stored as a JSON file in the `data/candidates/` directory. These files contain detailed information about the candidates, including personal details, education, work experience, skills, and certifications.

### 2. **Vectorization Process**

   - **SentenceTransformer Model:** Upon starting the application, the `SentenceTransformer` model (`all-MiniLM-L6-v2`) is loaded.
   - **Resume Vectorization:** All candidate resumes are loaded and vectorized. Each resume's text is concatenated and encoded into a numerical vector, which is stored for similarity comparison.
   - **Performance Logging:** The time taken to load and vectorize all resumes is measured and printed to the console for performance monitoring.

### 3. **Handling User Searches**

   - **Input Processing:** When an HR specialist inputs a job description and initiates a search, the input text is vectorized using the same `SentenceTransformer` model.
   - **Similarity Calculation:** The vectorized query is compared against all stored resume vectors using cosine similarity to determine how well each candidate matches the job description.
   - **Threshold Filtering:** Candidates with a similarity score below a predefined threshold (e.g., 60%) are excluded from the results.
   - **Ranking and Limiting:** The remaining candidates are sorted in descending order based on their similarity scores and limited to a maximum number of results (e.g., 20).

### 4. **Displaying Results**

   - **Pagination:** Search results are displayed in a paginated format, showing a limited number of candidates per page (e.g., 5) to enhance readability and navigation.
   - **Candidate Details:** Each candidate entry includes their name, match percentage, and an option to add them to the favorites list.
   - **Interactive Elements:** Users can view detailed profiles, add or remove favorites, and manage their search history directly from the interface.

### 5. **Favorites and History Management**

   - **Favorites:** Users can mark candidates as favorites, which are stored in the session. The favorites list can be accessed from the dedicated favorites page.
   - **Search History:** Each search query along with its results is saved in the session history, allowing users to revisit past searches. Users can also delete specific entries from their search history.

### 6. **Performance Monitoring**

   - **Request Timing:** The application logs the time taken to process each user request, aiding in performance optimization and monitoring.

## API Endpoints

### 1. **`/` (Landing Page)**

   - **Method:** GET
   - **Description:** Renders the landing page of the application.

### 2. **`/search` (Search Page)**

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

### 3. **`/history` (History Page)**

   - **Method:** GET
   - **Description:** Displays the history of past search queries and their results.

### 4. **`/delete_history` (Delete History Entry)**

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

### 5. **`/profile/<candidate_id>` (Candidate Profile Page)**

   - **Method:** GET
   - **Description:** Displays detailed information about a specific candidate.

### 6. **`/add_favorite` (Add Candidate to Favorites)**

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

### 7. **`/remove_favorite` (Remove Candidate from Favorites)**

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

### 8. **`/favorites` (Favorites Page)**

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

© 2024 BONFIRE TEAM. All rights reserved.

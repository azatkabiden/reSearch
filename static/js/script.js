// static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    // Обработчик кнопки "Найти"
    const searchButton = document.getElementById('search-button');
    const queryInput = document.getElementById('query');
    const resultsSection = document.getElementById('results');
    const candidatesList = document.getElementById('candidates-list');
    const loadingOverlay = document.getElementById('loading-overlay');
    const paginationControls = document.getElementById('pagination-controls');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');

    let allCandidates = []; 
    let currentPage = 1;
    const candidatesPerPage = 5;
    let totalPages = 1;

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const query = queryInput.value.trim();

            console.log('Кнопка "Найти" нажата.');

            if (query === '') {
                alert('Пожалуйста, введите описание идеального кандидата.');
                return;
            }

            console.log('Отправляем запрос на сервер:', query);

            // Показываем оверлей загрузки
            loadingOverlay.classList.remove('d-none');

            // Сброс пагинации
            currentPage = 1;

            // Отправка запроса на бэкэнд
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => {
                console.log('Ответ от сервера получен:', response);
                if (!response.ok) {
                    throw new Error('Сетевая ошибка при выполнении запроса.');
                }
                return response.json();
            })
            .then(data => {
                console.log('Данные от сервера:', data);
                allCandidates = data.candidates;
                totalPages = Math.ceil(allCandidates.length / candidatesPerPage);
                displayCurrentPage();
                updatePaginationControls();
            })
            .catch(error => {
                console.error('Ошибка при выполнении запроса:', error);
                alert('Произошла ошибка при выполнении поиска.');
            })
            .finally(() => {
                // Скрываем оверлей загрузки
                loadingOverlay.classList.add('d-none');
            });
        });
    }

    // Функция отображения текущей страницы
    function displayCurrentPage() {
        // Очистка предыдущих результатов
        candidatesList.innerHTML = '';

        if (allCandidates.length === 0) {
            candidatesList.innerHTML = '<div class="alert alert-warning text-center" role="alert">Нет подходящих кандидатов в базе данных.</div>';
            resultsSection.classList.remove('d-none');
            paginationControls.classList.add('d-none');
            return;
        }

        // Вычисляем индексы для текущей страницы
        const startIndex = (currentPage - 1) * candidatesPerPage;
        const endIndex = startIndex + candidatesPerPage;
        const candidatesToDisplay = allCandidates.slice(startIndex, endIndex);

        candidatesToDisplay.forEach(candidate => {
            const candidateItem = document.createElement('div');
            candidateItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center fade-in';

            const nameDiv = document.createElement('div');
            nameDiv.className = 'd-flex align-items-center';

            const h5 = document.createElement('h5');
            h5.className = 'mb-1 me-3';
            h5.style.fontSize = '1.25rem';
            h5.innerHTML = `<a href="/profile/${candidate.id}" target="_blank"><i class="bi bi-person me-2 text-success"></i>${candidate.FИО}</a>`;

            // Создаём бейдж с процентом совпадения
            const scoreBadge = document.createElement('span');
            scoreBadge.className = 'badge bg-primary ms-2';
            scoreBadge.textContent = `${candidate.score}%`;

            nameDiv.appendChild(h5);
            nameDiv.appendChild(scoreBadge);  // Добавляем бейдж к имени

            const favoriteBtn = document.createElement('button');
            favoriteBtn.className = 'btn btn-outline-success btn-sm';
            favoriteBtn.innerHTML = '<i class="bi bi-star-plus me-1"></i> Добавить в избранное';
            favoriteBtn.setAttribute('data-id', candidate.id);

            candidateItem.appendChild(nameDiv);
            candidateItem.appendChild(favoriteBtn);

            candidatesList.appendChild(candidateItem);
        });

        resultsSection.classList.remove('d-none');
        paginationControls.classList.remove('d-none');
    }

    // Обработчик кликов по кнопкам пагинации
    if (prevPageBtn && nextPageBtn) {
        prevPageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                displayCurrentPage();
                updatePaginationControls();
            }
        });

        nextPageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                displayCurrentPage();
                updatePaginationControls();
            }
        });
    }

    // Функция обновления состояния кнопок пагинации
    function updatePaginationControls() {
        if (currentPage <= 1) {
            prevPageBtn.classList.add('disabled');
        } else {
            prevPageBtn.classList.remove('disabled');
        }

        if (currentPage >= totalPages) {
            nextPageBtn.classList.add('disabled');
        } else {
            nextPageBtn.classList.remove('disabled');
        }
    }

    // Обработчик кликов по кнопкам
    document.body.addEventListener('click', (event) => {
        const target = event.target;

        // Обработка кнопок добавления в избранное
        if (target.closest('.btn-outline-success')) {
            const button = target.closest('.btn-outline-success');
            const candidateId = button.getAttribute('data-id');
            if (candidateId) {
                console.log(`Добавление кандидата в избранное: ID = ${candidateId}`);
                addFavorite(candidateId, button);
            } else {
                console.warn('Кнопка добавления в избранное не содержит data-id');
            }
        }

        // Обработка кнопок удаления записи из истории
        if (target.closest('.delete-history')) {
            const button = target.closest('.delete-history');
            const index = button.getAttribute('data-index');
            if (index !== null) {
                console.log(`Удаление записи из истории: Index = ${index}`);
                deleteHistoryEntry(index, button);
            } else {
                console.warn('Кнопка удаления из истории не содержит data-index');
            }
        }

        // Обработка кнопок удаления из избранного
        if (target.closest('.remove-favorite')) {
            const button = target.closest('.remove-favorite');
            const candidateId = button.getAttribute('data-id');
            if (candidateId) {
                console.log(`Удаление кандидата из избранного: ID = ${candidateId}`);
                removeFavorite(candidateId, button);
            } else {
                console.warn('Кнопка удаления из избранного не содержит data-id');
            }
        }

        // Обработка кнопки избранного на странице профиля
        if (target.closest('#favorite-button')) {
            const button = target.closest('#favorite-button');
            const candidateId = button.getAttribute('data-id');
            if (candidateId) {
                console.log(`Переключение избранного на профиле: ID = ${candidateId}`);
                toggleFavorite(candidateId, button);
            } else {
                console.warn('Кнопка избранного на профиле не содержит data-id');
            }
        }
    });

    // Функция добавления кандидата в избранное
    function addFavorite(candidateId, button) {
        fetch('/add_favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `candidate_id=${encodeURIComponent(candidateId)}`
        })
        .then(response => response.json())
        .then(data => {
            console.log('Результат добавления в избранное:', data);
            if (data.status === 'added') {
                button.classList.remove('btn-outline-success');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="bi bi-star-fill me-1"></i> В избранном';
            }
        })
        .catch(error => {
            console.error('Ошибка при добавлении в избранное:', error);
        });
    }

    // Функция удаления записи из истории
    function deleteHistoryEntry(index, button) {
        fetch('/delete_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `index=${encodeURIComponent(index)}`
        })
        .then(response => response.json())
        .then(data => {
            console.log('Результат удаления из истории:', data);
            if (data.status === 'success') {
                // Удаляем элемент из DOM
                const accordionItem = button.closest('.accordion-item');
                if (accordionItem) {
                    accordionItem.remove();
                } else {
                    console.error('Не удалось найти .accordion-item для удаления.');
                }
            } else {
                alert('Не удалось удалить запись из истории.');
            }
        })
        .catch(error => {
            console.error('Ошибка при удалении записи из истории:', error);
            alert('Произошла ошибка при удалении записи из истории.');
        });
    }

    // Функция удаления кандидата из избранного
    function removeFavorite(candidateId, button) {
        fetch('/remove_favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `candidate_id=${encodeURIComponent(candidateId)}`
        })
        .then(response => response.json())
        .then(data => {
            console.log('Результат удаления из избранного:', data);
            if (data.status === 'removed') {
                // Если кнопка находится на странице профиля
                if (button.id === 'favorite-button') {
                    button.classList.remove('btn-success');
                    button.classList.add('btn-outline-success');
                    button.innerHTML = '<i class="bi bi-star-plus-fill me-1"></i> Добавить в избранное';
                }
                // Если кнопка находится в списке избранных
                else {
                    const listGroupItem = button.closest('.list-group-item');
                    if (listGroupItem) {
                        listGroupItem.remove();
                    } else {
                        console.error('Не удалось найти .list-group-item для удаления.');
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при удалении из избранного:', error);
        });
    }

    // Функция переключения состояния избранного на странице профиля
    function toggleFavorite(candidateId, button) {
        if (button.classList.contains('btn-outline-success')) {
            addFavorite(candidateId, button);
        } else {
            removeFavorite(candidateId, button);
        }
    }
});

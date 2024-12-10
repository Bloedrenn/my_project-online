// Плавная прокрутка к началу страницы при смене пагинации
document.addEventListener('DOMContentLoaded', function() {
    // Функция для навешивания обработчиков на пагинационные ссылки
    function attachPaginationLinks() {
        // Находим все ссылки пагинации
        const paginationLinks = document.querySelectorAll('.pagination a.page-link');
        
        paginationLinks.forEach(function(link) {
            link.addEventListener('click', function(event) {
                // Предотвращаем стандартное поведение ссылки
                event.preventDefault();
                const url = this.getAttribute('href');
                if (url !== '#') {
                    // Обновляем URL без перезагрузки страницы
                    window.history.pushState(null, '', url);
                    // Выполняем AJAX-запрос для получения новой страницы
                    fetch(url, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.text())
                    .then(data => {
                        // Парсим полученные данные и заменяем содержимое <main>
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(data, 'text/html');
                        const newMain = doc.querySelector('main').innerHTML;
                        // Обновляем содержимое главного контейнера
                        document.querySelector('main').innerHTML = newMain;
                        
                        // Плавная прокрутка вверх страницы
                        window.scrollTo({
                            top: 0,
                            behavior: 'smooth'
                        });
                        
                        // Повторно навешиваем обработчики на новые пагинационные ссылки
                        attachPaginationLinks();
                    })
                    .catch(error => console.error('Ошибка при загрузке страницы:', error));
                }
            });
        });
    }
    // Инициализируем обработчики при первой загрузке страницы
    attachPaginationLinks();
});

// Обработчик кнопки лайка
document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('like-button');
    
    if (likeButton) {
        likeButton.addEventListener('click', function() {
            const postSlug = this.getAttribute('post-slug');
            const isAuthenticated = this.hasAttribute('user-authenticated');
            
            if (!isAuthenticated) {
                window.location.href = '/users/login/?next=' + window.location.pathname;
                return;
            }
            fetch(`/blog/post/${postSlug}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Обновляем состояние кнопки
                if (data.liked) {
                    this.classList.remove('not-liked');
                    this.classList.add('liked');
                    this.querySelector('i').classList.remove('bi-hand-thumbs-up');
                    this.querySelector('i').classList.add('bi-hand-thumbs-up-fill');
                } else {
                    this.classList.remove('liked');
                    this.classList.add('not-liked');
                    this.querySelector('i').classList.remove('bi-hand-thumbs-up-fill');
                    this.querySelector('i').classList.add('bi-hand-thumbs-up');
                }
                
                // Обновляем счетчик лайков
                document.getElementById('likes-count').textContent = data.likes_count;
            });
        });
    }
});
// Функция получения CSRF-токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
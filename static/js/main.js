// static/js/main.js

// Функция для анимации перехода между разделами
function animateTransition(element, callback) {
    element.style.opacity = 0;
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        element.style.opacity = 1;
        element.style.transform = 'translateY(0)';
        
        if (callback) {
            callback();
        }
    }, 100);
}

// Функция для отображения всплывающего сообщения
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        // Создаем контейнер для тостов, если его нет
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Создаем элемент toast
    const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);
    const toast = document.createElement('div');
    toast.className = `toast align-items-center border-0 ${type === 'error' ? 'bg-danger' : type === 'success' ? 'bg-success' : 'bg-info'} text-white`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Добавляем содержимое
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
        </div>
    `;
    
    // Добавляем toast в контейнер
    document.getElementById('toast-container').appendChild(toast);
    
    // Инициализируем и показываем toast
    const toastInstance = new bootstrap.Toast(toast, { 
        delay: 5000,
        animation: true
    });
    toastInstance.show();
    
    // Удаляем элемент после закрытия
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Обработчик событий при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Анимация для карточек на главной странице
    const mainMenuButtons = document.querySelectorAll('.main-menu-btn');
    mainMenuButtons.forEach((button, index) => {
        setTimeout(() => {
            animateTransition(button);
        }, index * 100);
    });
    
    // Инициализация тултипов
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Обработка отправки форм через AJAX
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                } else {
                    showToast(data.message || 'Произошла ошибка', 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                showToast('Произошла ошибка при отправке формы', 'error');
            });
        });
    });
    
    // Кнопка для возврата к началу страницы
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Обработка модальных окон
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input:not([type=hidden])');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
});

// Функция для предварительного просмотра загружаемого изображения
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewElement);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Функция для получения геолокации
function getLocation(outputElement) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Успешное получение позиции
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                
                const locationInput = document.getElementById(outputElement);
                if (locationInput) {
                    locationInput.value = `${latitude}, ${longitude}`;
                    showToast('Геолокация успешно получена', 'success');
                }
            },
            // Ошибка при получении позиции
            function(error) {
                let errorMessage = 'Не удалось получить вашу геолокацию';
                
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Вы отклонили запрос на получение геолокации';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Информация о местоположении недоступна';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Время ожидания получения геолокации истекло';
                        break;
                }
                
                showToast(errorMessage, 'error');
            }
        );
    } else {
        showToast('Ваш браузер не поддерживает геолокацию', 'error');
    }
}
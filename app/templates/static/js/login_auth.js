// login_auth.js — полная логика авторизации с валидацией и тостами

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.getElementById('togglePassword');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    // Создаем контейнер для тостов, если его нет
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    // Функция показа тостов
    window.showToast = function(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
        
        toast.addEventListener('click', () => toast.remove());
    };

    // Валидация формы
    function validateForm() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        if (!username) {
            showToast('Введите имя пользователя', 'error');
            usernameInput.focus();
            return false;
        }
        
        if (!password) {
            showToast('Введите пароль', 'error');
            passwordInput.focus();
            return false;
        }
        
        if (password.length < 6) {
            showToast('Пароль должен содержать минимум 6 символов', 'error');
            passwordInput.focus();
            return false;
        }
        
        if (password.length > 50) {
            showToast('Пароль слишком длинный (максимум 50 символов)', 'error');
            passwordInput.focus();
            return false;
        }
        
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(username)) {
            showToast('Имя пользователя может содержать только буквы, цифры и подчеркивание', 'error');
            usernameInput.focus();
            return false;
        }
        
        return true;
    }

    // Обработка отправки формы
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!validateForm()) {
                return;
            }
            
            const submitBtn = loginForm.querySelector('input[type="submit"]');
            const originalValue = submitBtn.value;
            submitBtn.value = 'Вход...';
            submitBtn.disabled = true;
            
            try {
                const formData = new FormData(loginForm);
                const response = await fetch(loginForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (response.status === 401) {
                    const data = await response.json().catch(() => ({}));
                    showToast(data.message || 'Неверное имя пользователя или пароль', 'error');
                } else if (response.status === 429) {
                    showToast('Слишком много попыток входа. Попробуйте позже', 'error');
                } else {
                    showToast('Ошибка сервера. Попробуйте позже', 'error');
                }
            } catch (error) {
                console.error('Login error:', error);
                showToast('Ошибка соединения с сервером', 'error');
            } finally {
                submitBtn.value = originalValue;
                submitBtn.disabled = false;
            }
        });
    }

    // Валидация при вводе
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            this.value = this.value.replace(/\s/g, '');
        });
    }

    // Индикатор сложности пароля
    if (passwordInput && strengthBar && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            strengthBar.className = 'strength-bar';
            
            if (password.length === 0) {
                strengthBar.style.width = '0';
                strengthText.textContent = '';
                return;
            }
            
            let strength = 0;
            
            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            if (/[A-Z]/.test(password)) strength += 0.5;
            if (/[0-9]/.test(password)) strength += 0.5;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            if (password.length < 6) {
                strengthBar.classList.add('weak');
                strengthText.textContent = 'Слишком простой';
            } else if (strength < 2) {
                strengthBar.classList.add('weak');
                strengthText.textContent = 'Слабый';
            } else if (strength < 3) {
                strengthBar.classList.add('medium');
                strengthText.textContent = 'Средний';
            } else {
                strengthBar.classList.add('strong');
                strengthText.textContent = 'Надёжный';
            }
        });
    }

    // Защита от XSS
    function sanitizeInput(input) {
        return input.replace(/[<>]/g, '');
    }

    usernameInput?.addEventListener('blur', function() {
        this.value = sanitizeInput(this.value);
    });

    // Enter для отправки
    passwordInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            loginForm.dispatchEvent(new Event('submit'));
        }
    });

    // Показ/скрытие пароля
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            toggleBtn.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
        });
    }
});
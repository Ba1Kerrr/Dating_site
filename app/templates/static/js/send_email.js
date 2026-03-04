// Получаем данные из формы
const email = document.querySelector('input[name="email"]').value;

// Отправляем запрос на сервер для проверки почты
fetch('/send_email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ email: email })
})
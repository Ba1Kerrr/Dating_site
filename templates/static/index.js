function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.innerText = message;
    notification.classList.remove('hidden');
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 500); // время, через которое уведомление будет скрыто
    }, 3000); // время отображения уведомления
}

// Пример использования
function validateForm() {
    // Здесь можно добавить вашу валидацию формы
    // Если все хорошо, показываем уведомление
    if (password == confirm_password){
        showNotification('Registration Successful!');
        return true; // Возвращаем true, чтобы форма отправилась
    }
    else{
        showNotification('Passwords do not match!');
        return false;
    }
}
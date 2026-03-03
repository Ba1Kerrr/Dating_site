    // Простая функция для тостов
    function showToast(message) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Анимация появления карточек
    document.querySelectorAll('.profile-card').forEach((card, index) => {
        card.style.animation = `fadeIn 0.4s ease ${index * 0.05}s both`;
    });
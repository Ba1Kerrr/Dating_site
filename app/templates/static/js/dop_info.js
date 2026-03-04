/* ============================================================
   dop_info.js — превью фото при выборе файла
   ============================================================ */

'use strict';

function previewAvatar(input) {
  const file = input.files[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    showToast('Только изображения (JPG, PNG, WebP)', 'error');
    input.value = '';
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    showToast('Файл слишком большой — максимум 5 МБ', 'error');
    input.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = function (e) {
    const img = document.getElementById('avatar-preview');
    const placeholder = document.getElementById('upload-placeholder');
    if (img) {
      img.src = e.target.result;
      img.classList.add('visible');
    }
    if (placeholder) placeholder.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

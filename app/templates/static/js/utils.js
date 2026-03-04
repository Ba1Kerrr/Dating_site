/* ============================================================
   utils.js — глобальные утилиты: тосты, санитайзер, хелперы
   Подключается на каждой странице
   ============================================================ */

'use strict';

/* ── Toast ──────────────────────────────────────────────── */
window.showToast = function(message, type = 'success', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  const remove = () => {
    toast.style.animation = 'toastOut .25s ease forwards';
    setTimeout(() => toast.remove(), 250);
  };

  const timer = setTimeout(remove, duration);
  toast.addEventListener('click', () => { clearTimeout(timer); remove(); });
};

/* ── Escape HTML (XSS) ──────────────────────────────────── */
window.escapeHtml = function(text) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(text)));
  return d.innerHTML;
};

/* ── Sanitize input (убираем < >) ───────────────────────── */
window.sanitizeInput = function(value) {
  return value.replace(/[<>]/g, '');
};

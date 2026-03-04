/* ============================================================
   index.js — главная страница: анимации, тосты
   Зависит от utils.js
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
  /* ── Staggered анимация карточек ────────────────────── */
  document.querySelectorAll('.profile-card').forEach(function (card, i) {
    card.style.animationDelay = (i * 50) + 'ms';
  });

  /* ── Блокировка запроса Chrome DevTools ─────────────── */
  const _fetch = window.fetch;
  window.fetch = function () {
    const url = arguments[0];
    if (typeof url === 'string' && url.includes('.well-known/appspecific')) {
      return Promise.resolve(new Response(null, { status: 404 }));
    }
    return _fetch.apply(this, arguments);
  };
});

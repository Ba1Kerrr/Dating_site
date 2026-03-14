/* ============================================================
   profile.js — редактирование профиля, музыкальный плеер-заглушка
   Зависит от utils.js
   ============================================================ */

'use strict';

/* ── Edit modal ─────────────────────────────────────────── */
function openEdit() {
  document.getElementById('edit-overlay')?.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeEdit() {
  document.getElementById('edit-overlay')?.classList.remove('open');
  document.body.style.overflow = '';
}

function closeEditOutside(e) {
  if (e.target === document.getElementById('edit-overlay')) closeEdit();
}

/* ── Music player (заглушка, замени на Spotify/VK API) ─── */
let _playing = false;

function togglePlay() {
  _playing = !_playing;
  const btn   = document.getElementById('play-btn');
  const cover = document.getElementById('music-cover');
  if (!btn || !cover) return;

  btn.textContent = _playing ? '⏸' : '▶';

  if (_playing) {
    cover.classList.add('spinning');
    const title  = document.getElementById('music-title');
    const artist = document.getElementById('music-artist');
    if (title)  title.textContent  = 'Подключи Spotify API';
    if (artist) artist.textContent = 'для реальных треков';
  } else {
    cover.classList.remove('spinning');
  }
}

/* ── Avatar preview в форме редактирования ──────────────── */
document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.querySelector('.edit-modal input[type="file"]');
  if (!fileInput) return;

  fileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file || !file.type.startsWith('image/')) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      const ring = document.querySelector('.avatar-ring img');
      if (ring) ring.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
});

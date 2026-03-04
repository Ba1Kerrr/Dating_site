/* ============================================================
   login_auth.js — валидация и отправка формы входа
   Зависит от utils.js
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const form        = document.getElementById('login-form');
  const userInput   = document.getElementById('username');
  const pwInput     = document.getElementById('password');
  const toggleBtn   = document.getElementById('togglePassword');
  const strengthBar = document.getElementById('strengthBar');
  const strengthTxt = document.getElementById('strengthText');

  if (!form) return;

  /* ── Показ / скрытие пароля ─────────────────────────── */
  if (toggleBtn && pwInput) {
    toggleBtn.addEventListener('click', function () {
      const isText = pwInput.type === 'text';
      pwInput.type = isText ? 'password' : 'text';
      toggleBtn.textContent = isText ? '👁' : '👁‍🗨';
    });
  }

  /* ── Индикатор сложности пароля ─────────────────────── */
  if (pwInput && strengthBar && strengthTxt) {
    pwInput.addEventListener('input', function () {
      const pw = this.value;
      strengthBar.className = 'strength-bar';

      if (!pw) { strengthBar.style.width = '0'; strengthTxt.textContent = ''; return; }

      let score = 0;
      if (pw.length >= 8)              score++;
      if (pw.length >= 12)             score++;
      if (/[A-Z]/.test(pw))           score += 0.5;
      if (/[0-9]/.test(pw))           score += 0.5;
      if (/[^A-Za-z0-9]/.test(pw))    score++;

      if (pw.length < 6 || score < 2) {
        strengthBar.classList.add('weak');
        strengthTxt.textContent = 'Слабый';
      } else if (score < 3) {
        strengthBar.classList.add('medium');
        strengthTxt.textContent = 'Средний';
      } else {
        strengthBar.classList.add('strong');
        strengthTxt.textContent = 'Надёжный';
      }
    });
  }

  /* ── Убираем пробелы из username ────────────────────── */
  if (userInput) {
    userInput.addEventListener('input', function () {
      this.value = this.value.replace(/\s/g, '');
    });
    userInput.addEventListener('blur', function () {
      this.value = sanitizeInput(this.value);
    });
  }

  /* ── Отправка по Enter ──────────────────────────────── */
  pwInput?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); form.dispatchEvent(new Event('submit')); }
  });

  /* ── Валидация ──────────────────────────────────────── */
  function validate() {
    const user = userInput?.value.trim() ?? '';
    const pw   = pwInput?.value.trim() ?? '';

    if (!user) { showToast('Введите имя пользователя', 'error'); userInput?.focus(); return false; }
    if (!/^[a-zA-Z0-9_]+$/.test(user)) {
      showToast('Только буквы, цифры и подчёркивание', 'error');
      userInput?.focus(); return false;
    }
    if (!pw)       { showToast('Введите пароль', 'error'); pwInput?.focus(); return false; }
    if (pw.length < 6) { showToast('Пароль слишком короткий (мин. 6 символов)', 'error'); pwInput?.focus(); return false; }
    return true;
  }

  /* ── Отправка формы ─────────────────────────────────── */
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!validate()) return;

    const submitBtn = form.querySelector('[type="submit"]');
    const origText  = submitBtn.value ?? submitBtn.textContent;
    submitBtn.disabled = true;
    if (submitBtn.tagName === 'INPUT') submitBtn.value = 'Входим...';
    else submitBtn.textContent = 'Входим...';

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' },
      });

      if (resp.redirected) {
        window.location.href = resp.url;
        return;
      }

      const handlers = {
        401: 'Неверное имя пользователя или пароль',
        403: 'Доступ запрещён',
        429: 'Слишком много попыток — подождите немного',
      };

      const msg = handlers[resp.status];
      if (msg) { showToast(msg, 'error'); return; }

      // Пробуем получить сообщение из JSON
      const data = await resp.json().catch(() => ({}));
      showToast(data.message ?? 'Что-то пошло не так', 'error');

    } catch {
      showToast('Нет связи с сервером', 'error');
    } finally {
      submitBtn.disabled = false;
      if (submitBtn.tagName === 'INPUT') submitBtn.value = origText;
      else submitBtn.textContent = origText;
    }
  });
});

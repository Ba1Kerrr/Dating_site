/* ============================================================
   register.js — отправка кода на email + валидация регистрации
   Зависит от utils.js
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const sendBtn    = document.getElementById('send-email-btn');
  const emailInput = document.getElementById('email');
  const statusEl   = document.getElementById('code-status');
  const form       = document.getElementById('register-form');
  const pwInput    = document.getElementById('password');
  const pw2Input   = document.getElementById('confirm_password');

  /* ── Отправка кода на email ─────────────────────────── */
  if (sendBtn && emailInput) {
    sendBtn.addEventListener('click', async function () {
      const email = emailInput.value.trim();

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setStatus('Введите корректный email', 'error');
        return;
      }

      sendBtn.disabled = true;
      setStatus('Отправляем код…', 'accent');

      try {
        const resp = await fetch('/register/send_email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });

        if (resp.ok) {
          setStatus(`✓ Код отправлен на ${email}`, 'success');
          startCooldown(60);
        } else {
          const data = await resp.json().catch(() => ({}));
          setStatus(data.message ?? 'Ошибка отправки — попробуйте снова', 'error');
          sendBtn.disabled = false;
        }
      } catch {
        setStatus('Нет связи с сервером', 'error');
        sendBtn.disabled = false;
      }
    });
  }

  function setStatus(text, type) {
    if (!statusEl) return;
    const colors = { success: 'var(--success)', error: 'var(--error)', accent: 'var(--accent)' };
    statusEl.style.color = colors[type] ?? 'var(--muted)';
    statusEl.textContent = text;
    statusEl.style.display = 'block';
  }

  /* ── Cooldown кнопки после отправки ─────────────────── */
  function startCooldown(sec) {
    if (!sendBtn) return;
    let left = sec;
    sendBtn.textContent = `${left}с`;
    const t = setInterval(() => {
      left--;
      if (left <= 0) {
        clearInterval(t);
        sendBtn.disabled = false;
        sendBtn.textContent = 'Код →';
      } else {
        sendBtn.textContent = `${left}с`;
      }
    }, 1000);
  }

  /* ── Валидация совпадения паролей ───────────────────── */
  if (pw2Input && pwInput) {
    pw2Input.addEventListener('input', function () {
      if (pwInput.value && this.value && pwInput.value !== this.value) {
        this.style.borderColor = 'var(--error)';
      } else {
        this.style.borderColor = '';
      }
    });
  }

  /* ── Убираем пробелы ────────────────────────────────── */
  document.getElementById('username')?.addEventListener('input', function () {
    this.value = this.value.replace(/\s/g, '');
  });

  /* ── Сабмит формы ───────────────────────────────────── */
  if (form) {
    form.addEventListener('submit', function (e) {
      if (pwInput && pw2Input && pwInput.value !== pw2Input.value) {
        e.preventDefault();
        showToast('Пароли не совпадают', 'error');
        pw2Input.focus();
      }
    });
  }
});

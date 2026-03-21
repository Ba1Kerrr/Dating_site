"""
app/celery_app.py
Celery-приложение. Импортируется и воркером, и FastAPI.

Структура очередей:
  emails   — отправка писем (регистрация, восстановление пароля)
  default  — прочие фоновые задачи
"""
import os
import json
import logging
from pathlib import Path

import requests as http_requests
from celery import Celery

logger = logging.getLogger(__name__)


BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "dating_site",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    broker_connection_retry_on_startup=True,
    timezone="Europe/Moscow",
    enable_utc=True,
    task_default_queue="default",
    task_routes={
        "celery_app.send_verification_email": {"queue": "emails"},
        "celery_app.send_password_reset_email": {"queue": "emails"},
        "celery_app.send_welcome_email": {"queue": "emails"},
        "celery_app.send_new_match_email": {"queue": "emails"},
        "celery_app.send_new_message_email": {"queue": "emails"},
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

BREVO_API_KEY = os.environ.get("Brevo_key", "")
BREVO_SERVER = "https://api.brevo.com/v3/smtp/email"
SENDER_EMAIL = os.environ.get("email", "")
SENDER_NAME = "SoulMates"

# Путь к шаблонам
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates" / "emails"


def _render_template(template_name: str, variables: dict) -> str:
    """Рендерит HTML шаблон из файла"""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        logger.error("Template not found: %s", template_path)
        return f"<p>Template not found: {template_name}</p>"
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    for key, value in variables.items():
        template = template.replace(f"{{{{ {key} }}}}", str(value))
    
    return template


def _send_brevo(to_email: str, subject: str, html_content: str) -> bool:
    """Низкоуровневая отправка через Brevo API с HTML."""
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    try:
        resp = http_requests.post(BREVO_SERVER, headers=headers, json=payload, timeout=10)
        if resp.status_code not in (200, 201):
            logger.error("Brevo error %s: %s", resp.status_code, resp.text)
            return False
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.error("Brevo request failed: %s", exc)
        return False


@celery_app.task(
    name="celery_app.send_verification_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="emails",
)
def send_verification_email(self, email: str, username: str, code: str, verification_link: str = None) -> dict:
    """
    Отправить код подтверждения регистрации.
    """
    logger.info("Sending verification email to %s", email)
    subject = "Подтверждение email — SoulMates"
    
    if verification_link:
        # Если есть ссылка — используем HTML с кнопкой
        html = _render_template("verification.html", {
            "title": "Подтверждение email",
            "icon": "❤️",
            "username": username,
            "link": verification_link
        })
    else:
        # Fallback на текстовый код
        html = f"""
        <html>
            <body>
                <h2>Код подтверждения</h2>
                <p>Привет, {username}!</p>
                <p>Ваш код подтверждения: <strong>{code}</strong></p>
                <p>Код действителен 10 минут.</p>
            </body>
        </html>
        """
    
    ok = _send_brevo(email, subject, html)
    if not ok:
        raise self.retry(exc=Exception("Brevo send failed"))
    return {"status": "sent", "email": email}


@celery_app.task(
    name="celery_app.send_password_reset_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="emails",
)
def send_password_reset_email(self, email: str, username: str, reset_link: str) -> dict:
    """
    Отправить ссылку для сброса пароля.
    """
    logger.info("Sending password reset email to %s", email)
    subject = "Сброс пароля — SoulMates"
    
    html = _render_template("reset_password.html", {
        "title": "Сброс пароля",
        "icon": "🔐",
        "username": username,
        "link": reset_link
    })
    
    ok = _send_brevo(email, subject, html)
    if not ok:
        raise self.retry(exc=Exception("Brevo send failed"))
    return {"status": "sent", "email": email}


@celery_app.task(
    name="celery_app.send_welcome_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="emails",
)
def send_welcome_email(self, email: str, username: str, profile_link: str) -> dict:
    """
    Приветственное письмо после верификации.
    """
    logger.info("Sending welcome email to %s", email)
    subject = "Добро пожаловать в SoulMates! 🎉"
    
    html = _render_template("welcome.html", {
        "title": "Добро пожаловать!",
        "icon": "🎉",
        "username": username,
        "link": profile_link
    })
    
    ok = _send_brevo(email, subject, html)
    if not ok:
        raise self.retry(exc=Exception("Brevo send failed"))
    return {"status": "sent", "email": email}


@celery_app.task(
    name="celery_app.send_new_match_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="emails",
)
def send_new_match_email(self, email: str, username: str, matched_user: str, chat_link: str) -> dict:
    """
    Уведомление о новом матче.
    """
    logger.info("Sending new match email to %s", email)
    subject = "У тебя новый матч! 💕"
    
    html = _render_template("new_match.html", {
        "title": "Новый матч!",
        "icon": "💕",
        "username": username,
        "matched_user": matched_user,
        "link": chat_link
    })
    
    ok = _send_brevo(email, subject, html)
    if not ok:
        raise self.retry(exc=Exception("Brevo send failed"))
    return {"status": "sent", "email": email}


@celery_app.task(
    name="celery_app.send_new_message_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="emails",
)
def send_new_message_email(self, email: str, username: str, sender: str, message_preview: str, chat_link: str) -> dict:
    """
    Уведомление о новом сообщении.
    """
    logger.info("Sending new message email to %s", email)
    subject = f"Новое сообщение от {sender}"
    
    html = _render_template("new_message.html", {
        "title": "Новое сообщение",
        "icon": "💬",
        "username": username,
        "sender": sender,
        "message_preview": message_preview[:100],
        "link": chat_link
    })
    
    ok = _send_brevo(email, subject, html)
    if not ok:
        raise self.retry(exc=Exception("Brevo send failed"))
    return {"status": "sent", "email": email}
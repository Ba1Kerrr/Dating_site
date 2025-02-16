import os
import requests
import json
import random
import logging

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Константы
BREVO_API_KEY = "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"
BREVO_SERVER = 'https://api.brevo.com/v3/smtp/email'
SENDER_EMAIL = 'ssfs9943@gmail.com'
SENDER_NAME = 'SoulMates'
SUBJECT = 'Verification'

def send_email(email):
    try:
        # Код для отправки письма
        text_content = key = str(random.randint(100000, 999999))

        # Настройки Brevo
        brevo_api_key = "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"
        brevo_server = "https://api.brevo.com/v3/smtp/email"

        # Данные для отправки письма
        subject = "Verification"
        
        # Создание запроса
        payload = json.dumps({
            "sender": {"name": "SoulMates", "email": "ssfs9943@gmail.com"},
            "to": [{"email": email}],
            "subject": subject,
            "textContent": text_content,
        })

        # Отправка запроса
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json",
        }

        response = requests.request("POST", brevo_server, headers=headers, data=payload)

        # Проверка ошибок
        if response.status_code != 200:
            logging.error(f'Ошибка отправки письма: {response.text}')
            return None

        # Возвращение ключа подтверждения или идентификатора сообщения
        logging.info(f'Письмо отправлено успешно. messageId: {response.json().get("messageId")}')
        return key

    except Exception as e:
        logging.error(f'Ошибка отправки письма: {e}')
        return None
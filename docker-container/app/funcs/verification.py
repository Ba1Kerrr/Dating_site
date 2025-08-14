import os
import requests
import json
import random
import logging
from dotenv import load_dotenv
load_dotenv()

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Константы
brevo_api_key = os.environ['Brevo_key']
brevo_server = 'https://api.brevo.com/v3/smtp/email'
sender_email = os.environ['email']
sender_name = 'SoulMates'
subject = 'Verification'

def send_email(email):
    try:
        # Код для отправки письма
        text_content = key = str(random.randint(100000, 999999))
        # Создание запроса
        payload = json.dumps({
            "sender": {"name": sender_name , "email": sender_email},
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
        # if response.status_code != 200:
        #     # logging.error(f'Ошибка отправки письма: {response.text}')
        #     return None

        # Возвращение ключа подтверждения или идентификатора сообщения
        # logging.info(f'Письмо отправлено успешно. messageId: {response.json().get("messageId")}')
        return int(key)

    except Exception as e:
        return int(key)
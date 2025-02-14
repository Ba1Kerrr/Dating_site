import requests
import json
import random
#-----------------------------------------------------------------------------------------------------------------------------
#                                           send_email

def send_email(email,text_content):
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
    return response.status_code
    #мы это сразу отправляем main.py который будет от js при нажатии на "отправить письмо" выдавать нам то что ввел user
#-----------------------------------------------------------------------------------------------------------------------------
#                                           create key
def generate_key():
    return random.randint(1000,9999)

#-----------------------------------------------------------------------------------------------------------------------------
#                                           marks

#тут у нас получается 4 этапа - 
# генерация ключа,
# отправка email'а,
# получение ключа от пользователя,
# проверка ключа

#-----------------------------------------------------------------------------------------------------------------------------
#                                          получение ключа от пользователя

# input = input("Введите ключ:")
#тут будет функция импортирующаяся от main.py

#-----------------------------------------------------------------------------------------------------------------------------
#                                          обработка

def verification(email):
    key = generate_key()
    print("Ваш ключ:", key)
    send_email(email, "Ваш ключ: " + str(key))
    user_input = input("Введите ключ:")
    user_key = input()
    # Проверяем ключ
    if user_key == str(key):
        return [True,("Ключ верный!")]
    else:
        return [False,("Ключ неверный!")]

print(verification())
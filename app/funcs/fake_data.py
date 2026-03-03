# seed_fake_data.py
# Запуск: python seed_fake_data.py
# Или внутри контейнера: docker compose run --rm api python seed_fake_data.py

import os
import sys
import random
import hashlib

sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv("app/settings/.env"))

DB_URL = os.environ["DATABASE_ROUTE"]
engine = create_engine(DB_URL, echo=False)

#Данные для генерации

CITIES = ["Moscow", "Saint Petersburg", "Kazan", "Novosibirsk", "Yekaterinburg"]

MALE_NAMES   = ["Alexei", "Dmitry", "Ivan", "Sergei", "Nikita",
                "Artem", "Pavel", "Mikhail", "Andrei", "Kirill"]
FEMALE_NAMES = ["Anna", "Maria", "Olga", "Natalia", "Elena",
                "Daria", "Irina", "Ksenia", "Yulia", "Polina"]

BIOS = [
    "Люблю путешествовать и пробовать новое",
    "Ищу интересного собеседника",
    "Обожаю кино и хорошую еду",
    "Спорт, музыка и хорошее настроение",
    "Работаю, отдыхаю, ищу смысл",
    "Котики, кофе и программирование",
    "Активный образ жизни и позитив",
    "Читаю книги, смотрю сериалы",
]

def fake_password():
    # bcrypt-хэш строки "password123" — не надо импортировать passlib
    # просто md5 для тестовых данных
    return hashlib.md5(b"password123").hexdigest()

def fake_avatar(username):
    return f"{username}-avatar.png"

def generate_users(n=50):
    users = []
    for i in range(n):
        gender = random.choice(["male", "female"])
        name   = random.choice(MALE_NAMES if gender == "male" else FEMALE_NAMES)
        city   = random.choice(CITIES)
        idx    = str(i).zfill(3)
        username = f"{name.lower()}_{idx}"
        email    = f"{username}@fakemail.com"

        users.append({
            "username": username,
            "email":    email,
            "password": fake_password(),
            "age":      random.randint(18, 40),
            "gender":   gender,
            "name":     name,
            "location": city,
            "avatar":   fake_avatar(username),
            "bio":      random.choice(BIOS),
        })
    return users

def generate_matches(user_ids, n=80):
    """Случайные пары — имитируем лайки/мэтчи"""
    matches = set()
    ids = list(user_ids)
    attempts = 0
    while len(matches) < n and attempts < n * 10:
        attempts += 1
        u1, u2 = random.sample(ids, 2)
        pair = (min(u1, u2), max(u1, u2))
        matches.add(pair)
    return list(matches)

#Сидирование

def seed(n_users=50, n_matches=80, clear=False):
    with engine.begin() as conn:

        if clear:
            print("Очищаем таблицы...")
            conn.execute(text("DELETE FROM matches"))
            conn.execute(text("DELETE FROM profile"))

        # Проверяем сколько уже есть
        existing = conn.execute(text("SELECT COUNT(*) FROM profile")).scalar()
        print(f"Уже в БД: {existing} пользователей")

        # Вставляем пользователей
        users = generate_users(n_users)
        inserted_users = 0
        for u in users:
            try:
                conn.execute(text("""
                    INSERT INTO profile
                        (username, email, password, age, gender, name, location, avatar, bio)
                    VALUES
                        (:username, :email, :password, :age, :gender, :name, :location, :avatar, :bio)
                    ON CONFLICT (username) DO NOTHING
                """), u)
                inserted_users += 1
            except Exception as e:
                print(f"  Пропуск {u['username']}: {e}")

        print(f"Добавлено пользователей: {inserted_users}")

        # Получаем id всех пользователей
        rows = conn.execute(text("SELECT id FROM profile")).fetchall()
        user_ids = [r[0] for r in rows]

        # Создаём таблицу matches если нет
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS matches (
                id        SERIAL PRIMARY KEY,
                user_id   INTEGER NOT NULL REFERENCES profile(id),
                target_id INTEGER NOT NULL REFERENCES profile(id),
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id, target_id)
            )
        """))

        # Вставляем мэтчи
        pairs = generate_matches(user_ids, n_matches)
        inserted_matches = 0
        for u1, u2 in pairs:
            try:
                conn.execute(text("""
                    INSERT INTO matches (user_id, target_id)
                    VALUES (:u1, :u2)
                    ON CONFLICT DO NOTHING
                """), {"u1": u1, "u2": u2})
                inserted_matches += 1
            except Exception as e:
                print(f"  Пропуск мэтча {u1}-{u2}: {e}")

        print(f"Добавлено мэтчей:        {inserted_matches}")
        print("Готово!")

        # Статистика
        total_users   = conn.execute(text("SELECT COUNT(*) FROM profile")).scalar()
        total_matches = conn.execute(text("SELECT COUNT(*) FROM matches")).scalar()
        print(f"\nИтого в БД: {total_users} пользователей, {total_matches} мэтчей")

        # Показываем пример
        sample = conn.execute(text(
            "SELECT username, gender, age, location FROM profile LIMIT 5"
        )).fetchall()
        print("\nПример пользователей:")
        for row in sample:
            print(f"  {row[0]:20} {row[1]:6} age={row[2]:2} city={row[3]}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--users",   type=int, default=50,    help="Сколько пользователей")
    parser.add_argument("--matches", type=int, default=80,    help="Сколько мэтчей")
    parser.add_argument("--clear",   action="store_true",     help="Очистить таблицы перед вставкой")
    args = parser.parse_args()

    seed(n_users=args.users, n_matches=args.matches, clear=args.clear)
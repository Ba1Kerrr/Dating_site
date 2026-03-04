# Dating Site API

REST API для сайта знакомств, построенный на FastAPI. Включает регистрацию с подтверждением email, JWT-аутентификацию, систему лайков и взаимных симпатий, чат в реальном времени через WebSocket и отдельный ML-микросервис для ранжирования пар.

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-green)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-80%2B%20passing-brightgreen)](./app/tests)
[![Coverage](https://img.shields.io/badge/Coverage-~85%25-brightgreen)](./htmlcov)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange)](/.github/workflows)

---

## Содержание

- [Возможности](#возможности)
- [Стек](#стек)
- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [API](#api)
- [Postman](#postman)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)

---

## Возможности

**Пользователи.** Регистрация с подтверждением email через Brevo, двухуровневая JWT-аутентификация (access + refresh токены), загрузка и редактирование аватара, восстановление пароля и логина.

**Поиск пар.** Фильтрация по локации и полу, лайки, взаимные симпатии. Список кандидатов ранжируется ML-моделью с учётом разницы в возрасте, города и пола.

**Чат.** WebSocket-соединения с историей сообщений (infinite scroll), отметки о прочтении, список диалогов с последним сообщением.

**Безопасность.** Параметризованные запросы, rate limiting на вход (5 попыток/мин), валидация загружаемых файлов (только изображения, макс. 5 MB), настроенный CORS. Сессии — для браузера, JWT — для API.

**ML-сервис.** Отдельный микросервис на порту 8001. Random Forest модель (`match_predictor.pkl`) обучается на данных из БД и предсказывает совместимость пользователей.

---

## Стек

| Компонент       | Технология                     |
|-----------------|--------------------------------|
| API Framework   | FastAPI 0.115.8                |
| База данных     | PostgreSQL 16 + SQLAlchemy 2.0 |
| Аутентификация  | JWT + SessionMiddleware        |
| ML              | scikit-learn, pandas, numpy    |
| Тестирование    | pytest, pytest-asyncio         |
| Контейнеры      | Docker, Docker Compose         |
| CI/CD           | GitHub Actions                 |
| Email           | Brevo API                      |
| Линтинг         | Ruff                           |

---

## Быстрый старт

### Docker (рекомендуется)

```bash
git clone https://github.com/Ba1Kerrr/Dating_site.git
cd Dating_site

cp app/settings/.env.example app/settings/.env
# Заполни .env своими данными

docker compose up -d
docker exec dating-api pytest tests/ -v
```

Запускаются три контейнера: `db` (PostgreSQL, порт 5432), `api` (FastAPI, порт 8000) и `ml` (ML-сервис, порт 8001).

### Вспомогательные скрипты

В папке `scripts/` есть готовые shell-скрипты для типовых операций: `setup.sh` — первоначальная настройка, `dev.sh` — запуск дев-сервера, `test.sh` — тесты, `db-migrate.sh` — миграции, `db-backup.sh` / `db-restore.sh` — резервные копии БД, `update_deps.sh` — обновление зависимостей, `clean.sh` — очистка.

---

## Переменные окружения

Создай файл `app/settings/.env`:

```env
# База данных
POSTGRES_DB=Dating_site
POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecret123
DATABASE_ROUTE=postgresql+psycopg2://postgres:supersecret123@db:5432/Dating_site

# Безопасность
SECRET_KEY=your-secret-key-here

# Email (Brevo)
Brevo_key=your-brevo-api-key
email=your-email@gmail.com
```

Зависимости разбиты по окружениям: `requirements.base.txt` — общие, `requirements.dev.txt` — для разработки, `requirements.prod.txt` — для продакшена, `requirements.ml.txt` — ML-сервис.

---

## API

Интерактивная документация: [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc) · [ML сервис](http://localhost:8001/docs)

### Аутентификация

| Метод  | Эндпоинт        | Описание                               |
|--------|-----------------|----------------------------------------|
| POST   | `/auth/token`   | Получить access + refresh токены       |
| POST   | `/auth/refresh` | Обновить access токен                  |
| GET    | `/auth/me`      | Данные текущего пользователя (Bearer)  |
| POST   | `/login`        | Войти через сессию (браузер)           |
| GET    | `/logout`       | Завершить сессию                       |

### Регистрация

| Метод  | Эндпоинт                 | Описание                            |
|--------|--------------------------|-------------------------------------|
| POST   | `/register`              | Создать аккаунт                     |
| POST   | `/register/dop-info`     | Заполнить профиль + загрузить фото  |
| POST   | `/register/send_email`   | Отправить код подтверждения         |

### Восстановление доступа

| Метод  | Эндпоинт            | Описание                       |
|--------|---------------------|--------------------------------|
| POST   | `/forgot/password`  | Сбросить пароль по username    |
| POST   | `/forgot/username`  | Восстановить доступ по email   |

### Профиль

| Метод  | Эндпоинт                   | Описание               |
|--------|----------------------------|------------------------|
| GET    | `/profile/{username}`      | Просмотр профиля       |
| POST   | `/profile/{username}/edit` | Редактирование профиля |

### Чат

| Метод  | Эндпоинт                        | Описание                         |
|--------|---------------------------------|----------------------------------|
| GET    | `/chat`                         | Список диалогов                  |
| GET    | `/chat/{companion}`             | Страница чата                    |
| GET    | `/chat/api/list`                | Список диалогов JSON (Bearer)    |
| GET    | `/chat/api/{companion}/history` | История сообщений JSON (Bearer)  |
| WS     | `/chat/ws/{companion}`          | WebSocket-соединение             |

### ML-сервис (порт 8001)

| Метод  | Эндпоинт  | Описание                         |
|--------|-----------|----------------------------------|
| GET    | `/health` | Проверка работоспособности       |
| POST   | `/train`  | Обучить модель на данных из БД   |
| POST   | `/rank`   | Ранжировать кандидатов для юзера |

---

## Postman

В `postman/collections/` лежит готовая коллекция `dating-site.postman_collection.json`. Глобальные переменные — в `postman/globals/workspace.postman_globals.json`.

Импортируй коллекцию через `Import` в Postman, выполни `POST /auth/token` — токен сохранится автоматически в переменную `{{token}}`.

---

## Тестирование

```bash
make test           # Все тесты
make test-cov       # С отчётом о покрытии
make test-smoke     # Только smoke
make test-last      # Перезапустить упавшие

open htmlcov/index.html   # Открыть отчёт (Mac)
start htmlcov/index.html  # Открыть отчёт (Windows)
```

Тесты разбиты по модулям: `test_auth.py`, `test_chat_and_auth.py`, `test_forgot.py`, `test_ml.py`, `test_profile.py`, `test_smoke.py`. Конфигурация — в `conftest.py` и `pytest.ini`.

---

## Структура проекта

```
Dating_site/
├── app/
│   ├── funcs/             # Утилиты: jwt_auth, hash, rate_limit, verification, filter
│   ├── ml/                # ML: features, model, train + сохранённая модель (models/)
│   ├── routers/           # Эндпоинты: auth, chat, forgot, login, logout, profile, registers
│   ├── database/          # Подключение и модели БД
│   ├── settings/          # .env и наборы зависимостей
│   ├── templates/         # HTML + static (CSS, JS, изображения)
│   ├── tests/             # pytest тесты
│   ├── utils/             # check_admin, security
│   ├── main.py
│   └── ml_service.py
├── postman/
│   ├── collections/
│   └── globals/
├── scripts/               # shell-скрипты для dev/ops задач
├── .github/
│   ├── workflows/ci.yml
│   └── ISSUE_TEMPLATE/
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.ml
├── Makefile
└── README.md
```

---

## Контакты

Автор: [Ba1Kerrr](https://github.com/Ba1Kerrr) — ssfs9943@gmail.com

Баги и предложения: [GitHub Issues](https://github.com/Ba1Kerrr/Dating_site/issues)
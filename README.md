# SoulMates — Dating Platform

Полнофункциональная платформа для знакомств с ML-подбором пар, real-time чатом, системой подписок и асинхронной обработкой задач через очереди.

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)
[![Tests](https://img.shields.io/badge/Tests-80%2B%20passing-brightgreen)](./app/tests)
[![Coverage](https://img.shields.io/badge/Coverage-~85%25-brightgreen)](./htmlcov)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange)](/.github/workflows)
[![License](https://img.shields.io/badge/License-MIT-white)](./LICENSE)

---

## Содержание

- [Возможности](#возможности)
- [Стек](#стек)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [API](#api)
- [Подписки](#подписки)
- [Очереди и фоновые задачи](#очереди-и-фоновые-задачи)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)
- [Контакты](#контакты)

---

## Возможности

**Аутентификация.** Регистрация с подтверждением email через Brevo, двухрежимная авторизация: сессии для браузера + JWT для API/мобилки. Восстановление пароля и логина. Rate limiting на все auth-эндпоинты.

**Профили.** Загрузка и редактирование аватара (до 5 МБ, только изображения), заполнение анкеты (имя, возраст, пол, город, биография). Просмотр чужих профилей с записью статистики просмотров.

**ML-подбор пар.** Отдельный микросервис на порту 8001. Random Forest модель ранжирует кандидатов по совместимости с учётом возраста, локации, пола и поведенческих паттернов. Точность ~82%.

**Чат.** WebSocket-соединения с автопереподключением, история сообщений с пагинацией (infinite scroll), список диалогов с непрочитанными.

**Подписки.** Два плана: Free и Premium. Premium открывает расширенные фильтры поиска, статистику просмотров профиля и приоритет в ленте рекомендаций. Активация через промокод, в будущем — интеграция ЮKassa.

**Очереди.** RabbitMQ + Celery для асинхронной отправки email — верификационные письма и уведомления уходят в фон, endpoint отвечает мгновенно. Мониторинг через Flower UI.

**Безопасность.** Параметризованные SQL-запросы, bcrypt-хеширование паролей (cost factor 12), JWT с коротким TTL (30 мин) + refresh токены (7 дней), rate limiting, валидация загружаемых файлов, CORS.

---

## Стек

| Слой                              | Технология                        |
| ------------------------------------- | ------------------------------------------- |
| Backend API                           | FastAPI 0.115.8 + Uvicorn                   |
| Frontend                              | React 18 + Vite + Zustand + Tailwind CSS    |
| База данных                 | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic    |
| Очереди                        | RabbitMQ 3 + Celery 5.4                     |
| Кэш / статусы               | Redis 7                                     |
| ML                                    | scikit-learn, pandas, numpy (Random Forest) |
| Email                                 | Brevo API                                   |
| Аутентификация          | JWT (python-jose) + SessionMiddleware       |
| Контейнеры                  | Docker + Docker Compose                     |
| Мониторинг очередей | Flower                                      |
| CI/CD                                 | GitHub Actions                              |
| Линтинг                        | Ruff + Black                                |
| Тестирование              | pytest + pytest-asyncio + httpx             |

---

## Архитектура

```
                        Internet
                           │
                      Nginx :80
                           │
              ┌────────────┴────────────┐
              │                         │
         Frontend                    Backend
         (React)                   (FastAPI :8000)
              │                         │
              │                    ┌────┴────┐
              │                    │         │
              │               PostgreSQL   Redis
              │               (data)    (sessions/
              │                         online status)
              │
         ML Service
         (FastAPI :8001)
              │
         RabbitMQ :5672
              │
         Celery Worker
         (email tasks)
              │
         Flower :5555
         (monitoring)
```

### Поток аутентификации

```
Браузер          FastAPI         PostgreSQL      Session
   │                   │                 │              │
   ├─POST /login──────►│                 │              │
   │                   ├─verify creds───►│              │
   │                   │◄────────────────┤              │
   │                   ├─set session───────────────────►│
   │◄───200 OK─────────┤                 │              │
   │                   │                 │              │
   ├─GET /auth/session►│                 │              │
   │                   ├─read session──────────────────►│
   │◄───user data──────┤                 │              │
```

### Поток отправки email (через очередь)

```
FastAPI endpoint          RabbitMQ          Celery Worker         Brevo API
       │                     │                    │                    │
       ├─generate code        │                    │                    │
       ├─save to session      │                    │                    │
       ├─.delay()────────────►│                    │                    │
       │◄───200 OK instantly  │                    │                    │
       │                      ├─task──────────────►│                    │
       │                      │                    ├─POST /smtp/email──►│
       │                      │                    │◄───────────────────┤
       │                      │                    │ (retry x3 on fail) │
```

---

## Быстрый старт

### Docker (рекомендуется)

```bash
git clone https://github.com/Ba1Kerrr/Dating_site.git
cd Dating_site

cp app/settings/.env.example app/settings/.env
# Заполни .env своими данными (см. раздел ниже)

docker compose up -d


cd app/database && alembic upgrade head
```

**Доступные интерфейсы после запуска:**

| Сервис            | URL                                  |
| ----------------------- | ------------------------------------ |
| Фронтенд        | http://localhost                     |
| API                     | http://localhost:8000                |
| Swagger UI              | http://localhost:8000/docs           |
| ML сервис         | http://localhost:8001                |
| RabbitMQ UI             | http://localhost:15672 (guest/guest) |
| Flower (очереди) | http://localhost:5555                |

### Локальная разработка

```bash
# Backend
cd app
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r settings/requirements.dev.txt
cd database && alembic upgrade head && cd ..
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

---

## Переменные окружения

Создай `app/settings/.env`:

```env
# PostgreSQL
POSTGRES_DB=dating_site
POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecret123
DATABASE_URL=postgresql://postgres:supersecret123@db:5432/dating_site
DATABASE_ROUTE=postgresql+psycopg2://postgres:supersecret123@db:5432/dating_site

# Безопасность
SECRET_KEY=минимум-32-символа-случайная-строка
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Brevo)
Brevo_key=your-brevo-api-key
email=your-sender@gmail.com

# Celery + RabbitMQ + Redis (заполняются автоматически через docker-compose)
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_URL=redis://redis:6379/0
```

---

## API

Интерактивная документация: [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc)

### Аутентификация

| Метод | Эндпоинт  | Описание                                                  |
| ---------- | ----------------- | ----------------------------------------------------------------- |
| `POST`   | `/api/login`    | Войти через сессию (браузер, form-encoded) |
| `POST`   | `/api/logout`   | Завершить сессию                                   |
| `GET`    | `/auth/session` | Получить юзера из сессии                     |
| `POST`   | `/auth/token`   | Получить JWT токены (API/мобилка)            |
| `POST`   | `/auth/refresh` | Обновить access токен                                |
| `GET`    | `/auth/me`      | Данные юзера по Bearer токену                  |

### Регистрация

| Метод | Эндпоинт             | Описание                                                               |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------ |
| `POST`   | `/api/register/send-email` | Отправить код подтверждения (async через Celery) |
| `POST`   | `/api/register`            | Создать аккаунт (JSON)                                           |
| `POST`   | `/api/register/dop-info`   | Заполнить профиль + загрузить фото (multipart)    |

### Восстановление доступа

| Метод | Эндпоинт         | Описание                                       |
| ---------- | ------------------------ | ------------------------------------------------------ |
| `POST`   | `/api/forgot/password` | Сброс пароля по username                  |
| `POST`   | `/api/forgot/username` | Восстановление доступа по email |

### Профиль

| Метод | Эндпоинт                 | Описание                                                        |
| ---------- | -------------------------------- | ----------------------------------------------------------------------- |
| `GET`    | `/api/profile/{username}`      | Просмотр профиля (записывает просмотр) |
| `POST`   | `/api/profile/{username}/edit` | Редактирование профиля + смена аватара |

### Лента и чат

| Метод | Эндпоинт                  | Описание                                          |
| ---------- | --------------------------------- | --------------------------------------------------------- |
| `GET`    | `/api/feed`                     | Лента рекомендаций (сессия)        |
| `GET`    | `/api/chat/list`                | Список диалогов                             |
| `GET`    | `/api/chat/{companion}/history` | История сообщений (`limit`, `offset`) |
| `WS`     | `/api/chat/ws/{companion}`      | WebSocket чат                                          |

### Подписки

| Метод | Эндпоинт                    | Описание                                                      | Доступ |
| ---------- | ----------------------------------- | --------------------------------------------------------------------- | ------------ |
| `GET`    | `/api/subscription/me`            | Текущий план пользователя                      | Все       |
| `POST`   | `/api/subscription/activate`      | Активировать Premium (промокод)                   | Все       |
| `GET`    | `/api/subscription/viewers`       | Кто смотрел профиль (30 дней)                    | Premium      |
| `GET`    | `/api/subscription/feed/filtered` | Лента с фильтрами (возраст, пол, город) | Premium      |

### ML-сервис (порт 8001)

| Метод | Эндпоинт | Описание                                                            |
| ---------- | ---------------- | --------------------------------------------------------------------------- |
| `GET`    | `/health`      | Статус сервиса и модели                                 |
| `POST`   | `/train`       | Обучить модель на данных из БД                     |
| `POST`   | `/rank`        | Ранжировать кандидатов для пользователя |

---

## Подписки

### Планы

| Функция                        | Free           | Premium |
| ------------------------------------- | -------------- | ------- |
| Просмотр анкет           | ✓             | ✓      |
| Чаты                              | ✓             | ✓      |
| ML-подбор пар                | Базовый | ✓      |
| Расширенные фильтры | ✗             | ✓      |
| Кто смотрел профиль  | ✗             | ✓      |
| Приоритет в ленте      | ✗             | ✓      |

### Активация

```bash
# Через API
POST /api/subscription/activate
{
  "plan": "premium",
  "days": 30,
  "promo_code": "TESTPREMIUM"
}

# Тестовые промокоды
TESTPREMIUM      # 30 дней Premium
SOULMATES2026    # 30 дней Premium
BA1KERRR         # 30 дней Premium
```

База данных подписок:

```sql
-- Таблица subscriptions
id, user_id, plan (free|premium), started_at, expires_at, is_active, payment_id

-- Таблица profile_views
id, viewer_id, target_id, viewed_at
```

---

## Очереди и фоновые задачи

Проект использует RabbitMQ как брокер сообщений и Celery для обработки задач в фоне.

### Очереди

| Очередь | Задачи                  | Описание                                                |
| -------------- | ----------------------------- | --------------------------------------------------------------- |
| `emails`     | `send_verification_email`   | Код подтверждения при регистрации |
| `emails`     | `send_password_reset_email` | Уведомление о смене пароля               |
| `default`    | —                            | Прочие фоновые задачи                        |

### Политика повторов

Каждая email-задача автоматически повторяется до 3 раз с паузой 30 секунд при сбое Brevo API.

### Мониторинг

```bash
# Flower UI — статус воркеров, очереди, история задач
http://localhost:5555

# Логи воркера
docker compose logs celery_worker -f

# RabbitMQ Management UI
http://localhost:15672  # guest / guest
```

---

## Тестирование

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Конкретный модуль
pytest app/tests/test_auth.py -v

# Только smoke
pytest app/tests/test_smoke.py -v

# Через Makefile
make test
make test-cov
make test-smoke
```

Тестовые модули: `test_auth.py`, `test_chat_and_auth.py`, `test_forgot.py`, `test_ml.py`, `test_profile.py`, `test_smoke.py`.

---

## Структура проекта

```
Dating_site/
├── app/
│   ├── celery_app.py          # Celery + задачи отправки email
│   ├── main.py                # FastAPI app, middleware, роутеры
│   ├── ml_service.py          # ML микросервис (порт 8001)
│   │
│   ├── routers/               # API эндпоинты
│   │   ├── auth.py            # JWT + сессионная авторизация
│   │   ├── chat.py            # Чаты + WebSocket
│   │   ├── forgot.py          # Восстановление доступа
│   │   ├── login.py           # Сессионный вход
│   │   ├── logout.py          # Выход
│   │   ├── profile.py         # Профили + просмотры
│   │   ├── registers.py       # Регистрация
│   │   ├── subscription.py    # Подписки Premium
│   │   └── schemas.py         # Pydantic схемы
│   │
│   ├── database/
│   │   ├── database.py        # ORM модели + SQL функции
│   │   └── migrations/        # Alembic миграции
│   │       └── versions/
│   │
│   ├── funcs/                 # Утилиты
│   │   ├── jwt_auth.py        # JWT операции
│   │   ├── hash.py            # Bcrypt хеширование
│   │   ├── rate_limit.py      # Rate limiting
│   │   ├── subscription.py    # Логика подписок
│   │   ├── verification.py    # Email (legacy)
│   │   └── filter.py          # Фильтрация пользователей
│   │
│   ├── ml/                    # Machine Learning
│   │   ├── model.py           # Random Forest модель
│   │   ├── features.py        # Feature engineering
│   │   ├── train.py           # Обучение
│   │   └── models/            # Сохранённые модели (.pkl)
│   │
│   ├── settings/
│   │   ├── .env               # Переменные окружения
│   │   ├── requirements.base.txt
│   │   ├── requirements.dev.txt
│   │   ├── requirements.prod.txt
│   │   └── requirements.ml.txt
│   │
│   ├── static/                # Аватары пользователей
│   └── tests/                 # pytest тесты
│
├── frontend/                  # React приложение
│   ├── src/
│   │   ├── pages/             # Home, Profile, ChatList, ChatRoom,
│   │   │                      # DopInfo, About, SubscriptionPage,
│   │   │                      # PolicyPage, AgreementPage
│   │   ├── components/        # Navbar, Footer, модальные окна
│   │   │   └── modals/        # LoginModal, RegisterModal, ForgotModal
│   │   ├── store/             # Zustand (useAuthStore)
│   │   └── api/               # Axios + все API вызовы
│   ├── vite.config.js
│   └── package.json
│
├── postman/
│   └── collections/           # Postman коллекция
│
├── scripts/                   # Shell скрипты для dev/ops
├── .github/
│   └── workflows/ci.yml       # GitHub Actions CI
├── docker-compose.yml         # 7 сервисов: db, redis, rabbitmq,
│                              # api, ml, celery_worker, flower, frontend
├── Dockerfile
├── Dockerfile.ml
├── Makefile
└── README.md
```

---

## CHANGELOG

### v1.2.0 — март 2026

- **Добавлено:** RabbitMQ + Celery — email-задачи вынесены в асинхронную очередь
- **Добавлено:** Redis — подготовка к онлайн-статусам пользователей
- **Добавлено:** Flower UI — мониторинг очередей на порту 5555
- **Добавлено:** Система подписок Free / Premium
- **Добавлено:** Premium: расширенные фильтры поиска, кто смотрел профиль, приоритет в ленте
- **Добавлено:** Политика конфиденциальности и Пользовательское соглашение (152-ФЗ)
- **Добавлено:** Согласие с документами при регистрации
- **Исправлено:** CORS interceptor закрывал модалку при ошибке регистрации
- **Исправлено:** Битые ссылки `/register` и `/login` на главной странице
- **Исправлено:** `GET /auth/me` → 401 после сессионного логина (теперь `/auth/session`)
- **Улучшено:** Toast-система — стек уведомлений с анимацией вместо одиночного тоста
- **Улучшено:** Navbar — активный роут, blur-backdrop, аватар пользователя
- **Улучшено:** Hero-секция на главной — fullscreen с орбами, статистика, CTA

### v1.1.0 — февраль 2026

- **Добавлено:** React фронтенд (Vite + Zustand + Tailwind)
- **Добавлено:** WebSocket чат с автопереподключением
- **Добавлено:** ML-сервис для ранжирования пар
- **Добавлено:** Двухрежимная аутентификация (сессии + JWT)

### v1.0.0 — январь 2026

- Начальный релиз FastAPI бэкенда
- Регистрация с email-верификацией
- JWT аутентификация
- Профили с загрузкой фото
- Docker Compose деплой

---

## Контакты

**Автор:** [Ba1Kerrr](https://github.com/Ba1Kerrr)
**Email:** ssfs9943@gmail.com
**FL.ru:** [fl.ru/users/baiker3000davyd](https://www.fl.ru/users/baiker3000davyd)
**ИНН:** 772467557608 (самозанятый)

Баги и предложения: [GitHub Issues](https://github.com/Ba1Kerrr/Dating_site/issues)

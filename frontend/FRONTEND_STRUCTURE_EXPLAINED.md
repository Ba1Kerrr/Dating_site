# 📱 Структура Фронтенда Dating Site - Полный разбор

## 🎯 Что здесь?

Это **React приложение** на **Vite** с **TailwindCSS**, собирается в Docker и раздается через Nginx.

---

## 📁 Файловая структура

```
frontend/
├── src/
│   ├── pages/           # Страницы приложения
│   │   ├── Home.jsx     # Главная страница (поиск профилей)
│   │   ├── About.jsx    # О приложении / справка
│   │   ├── Profile.jsx  # Профиль пользователя
│   │   ├── ChatList.jsx # Список чатов
│   │   ├── ChatRoom.jsx # Конкретный чат
│   │   └── DopInfo.jsx  # Доп информация при регистрации
│   │
│   ├── components/      # Переиспользуемые компоненты
│   │   └── PrivateRoute.jsx  # Защита маршрутов (логин проверка)
│   │
│   ├── store/           # Zustand хранилище (state management)
│   │   └── useAuthStore.js   # Состояние авторизации
│   │
│   ├── api/             # API запросы
│   │   └── client.js    # Axios конфиг для запросов к backend
│   │
│   ├── App.jsx          # Главный компонент приложения
│   ├── main.jsx         # Точка входа React
│   ├── index.css        # Глобальные стили + TailwindCSS
│   └── App.css          # Стили для App компонента
│
├── public/              # Статические файлы
│   └── (иконки, картинки и т.д.)
│
├── Dockerfile           # Docker конфиг для сборки
├── nginx.conf          # Конфиг nginx для раздачи статики
├── package.json        # Зависимости и скрипты
├── vite.config.js      # Конфиг Vite (бандлер)
├── postcss.config.js   # Конфиг PostCSS (для TailwindCSS)
├── eslint.config.js    # Конфиг ESLint (проверка кода)
├── index.html          # HTML шаблон
└── .env.production     # Переменные для продакшена
```

---

## 🔍 Разбор ключевых файлов

### 1️⃣ package.json - Зависимости и команды

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "type": "module",           // ← ES модули (import/export)
  "scripts": {
    "dev": "vite",           // npm run dev - локальная разработка
    "build": "vite build",   // npm run build - сборка для продакшена
    "lint": "eslint .",      // npm run lint - проверка кода
    "preview": "vite preview" // предпросмотр собранного приложения
  },
  "dependencies": {
    "axios": "^1.13.6",              // HTTP клиент для запросов
    "react": "^19.2.4",              // React фреймворк
    "react-dom": "^19.2.4",          // React для браузера
    "react-router-dom": "^7.13.1",   // Маршрутизация (переходы между страницами)
    "zustand": "^5.0.12"             // State management (хранилище состояния)
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^6.0.0", // Плагин Vite для React
    "@tailwindcss/postcss": "^4.2.2", // TailwindCSS (CSS фреймворк)
    "tailwindcss": "^4.2.2",
    "@eslint/js": "^9.39.4",          // ESLint для проверки кода
    "eslint-plugin-react-hooks": "^7.0.1",
    "vite": "^8.0.0"                  // Vite (бандлер/сборщик)
  }
}
```

**Главные зависимости:**
- **React** - UI фреймворк
- **react-router-dom** - навигация между страницами
- **axios** - запросы к API
- **zustand** - управление состоянием (где хранится info о пользователе и т.д.)
- **TailwindCSS** - стили (альтернатива CSS)
- **Vite** - быстрый бандлер (вместо Webpack)

---

### 2️⃣ vite.config.js - Конфиг сборщика

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],  // Включаем поддержку React (JSX)
})
```

**Что это делает:**
- Говорит Vite что это React приложение
- Включает поддержку JSX синтаксиса
- Настраивает быструю пересборку при изменении кода (HMR)

---

### 3️⃣ App.jsx - Главный компонент

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { PrivateRoute } from './components'
import useAuthStore from './store/useAuthStore'

import Home from './pages/Home'
import About from './pages/About'
// ... и другие страницы

function App() {
  const { fetchMe } = useAuthStore()  // Получает функцию из хранилища

  useEffect(() => { 
    fetchMe()  // При загрузке приложения - проверяет кто авторизован
  }, [])

  return (
    <BrowserRouter>                    {/* Включаем маршрутизацию */}
      <Routes>
        {/* Публичные маршруты (без авторизации) */}
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />

        {/* Приватные маршруты (нужна авторизация) */}
        <Route path="/register/dop-info" 
          element={<PrivateRoute><DopInfo /></PrivateRoute>} />
        <Route path="/chat" 
          element={<PrivateRoute><ChatList /></PrivateRoute>} />
        <Route path="/chat/:companion" 
          element={<PrivateRoute><ChatRoom /></PrivateRoute>} />
        <Route path="/users/:username" 
          element={<PrivateRoute><Profile /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

**Маршруты (Routes):**
- `/` - Главная (поиск профилей, регистрация/логин)
- `/about` - О приложении
- `/register/dop-info` - Доп информация при регистрации
- `/chat` - Список чатов (приватный)
- `/chat/:companion` - Конкретный чат с companion_id
- `/users/:username` - Профиль пользователя (приватный)

**PrivateRoute** - компонент который:
1. Проверяет авторизован ли пользователь
2. Если да - показывает страницу
3. Если нет - редиректит на логин

---

### 4️⃣ main.jsx - Точка входа

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Что это делает:**
1. Находит элемент `<div id="root"></div>` в index.html
2. Рендерит туда React компонент App
3. `React.StrictMode` - режим разработки с дополнительными проверками

---

### 5️⃣ index.html - HTML шаблон

```html
<div id="root"></div>
<script type="module" src="/src/main.jsx"></script>
```

**Это:**
- `<div id="root">` - контейнер куда рендерится React
- `<script type="module">` - говорит браузеру что это ES модуль

**В браузере рендерится:**
```
<div id="root">
  [Здесь рендерится весь React код из App.jsx]
</div>
```

---

### 6️⃣ index.css - Глобальные стили

```css
@import url('https://fonts.googleapis.com/css2?family=...');
@import "tailwindcss";

@theme {
  --font-unbounded: 'Unbounded', sans-serif;
  --font-onest: 'Onest', sans-serif;
}

* { box-sizing: border-box; }
body { font-family: 'Onest', sans-serif; }
```

**Что здесь:**
- Импорт шрифтов с Google Fonts
- Импорт TailwindCSS (утилиты для стилизации)
- Кастомные CSS переменные для шрифтов
- Глобальные стили для всей страницы

---

### 7️⃣ Dockerfile - Сборка приложения

```dockerfile
# Этап 1: Сборка
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                    # Установка точных версий зависимостей
COPY . .
RUN npm run build             # Собирает React в /dist

# Этап 2: Production
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html  # Копирует собранный код
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Как это работает:**

```
1. Берет Node.js образ
2. Устанавливает npm зависимости
3. Запускает npm run build
   ↓
   Vite собирает React в папку /dist/
   (минификация, оптимизация, один HTML файл)
4. Берет nginx образ
5. Копирует /dist в /usr/share/nginx/html
6. Запускает nginx который раздает статические файлы
```

**Результат:**
- Все .jsx файлы → один/несколько .js файлов
- Все CSS → оптимизированный CSS
- Все в /dist папке
- nginx раздает всё на порту 80

---

### 8️⃣ nginx.conf - Конфиг веб-сервера

```nginx
server {
    listen 80;
    server_name _;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;  # ← SPA routing
    }

    location /api {
        proxy_pass http://api:8000;        # Проксирует /api запросы к backend
        proxy_set_header Host $host;
    }
}
```

**Что это делает:**
1. Слушает порт 80
2. `/` запросы → раздает файлы из `/usr/share/nginx/html`
3. `try_files` → если файл не найден, отправляет `/index.html` (SPA routing)
4. `/api` запросы → перенаправляет к backend API на `http://api:8000`

**Это нужно для:**
- SPA (Single Page Application) - всегда первой загружать index.html
- Проксирования запросов к backend без CORS проблем

---

## 🔄 Как всё работает вместе

### Локальная разработка (npm run dev)

```
1. npm run dev
   ↓
2. Vite запускает dev сервер на http://localhost:5173
   ↓
3. Vite смотрит за изменениями в .jsx файлах
   ↓
4. При изменении - быстро пересобирает (HMR)
   ↓
5. Браузер показывает новый результат
```

**Преимущества:**
- Очень быстрая пересборка (секунды)
- Hot reload (не нужно рефрешить)
- Source maps (в DevTools видишь оригинальный код)
- Подробные ошибки

---

### Docker запуск (docker compose up)

```
1. docker compose up -d frontend
   ↓
2. Docker собирает Dockerfile
   ↓
3. npm install - устанавливает зависимости
   ↓
4. npm run build - собирает React в /dist
   ↓
5. Копирует /dist в nginx контейнер
   ↓
6. nginx раздает статику на http://localhost:80
```

**Результат:**
- Оптимизированное приложение
- Только статические файлы (HTML, JS, CSS)
- Быстрая загрузка
- Готово к production

---

## 🔌 Связь с Backend

### Запросы к API

Где-то в компоненте:

```javascript
import axios from 'axios'

// Получает API URL из переменной окружения
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL
})

// Запрос к backend
const response = await api.get('/api/users')
// ↑ Полный URL: http://localhost:8000/api/users
```

**Переменная окружения** `VITE_API_URL`:
- Локально: `http://localhost:8000`
- В Docker: `http://api:8000`
- На production: `https://api.example.com`

**В docker-compose.yml:**
```yaml
frontend:
  environment:
    - VITE_API_URL=http://api:8000
```

---

## 📊 Процесс разработки

### День 1: Ты пишешь компонент

```
1. Создаешь файл src/pages/MyPage.jsx
2. npm run dev
3. Vite перекомпилирует за 100ms
4. Видишь результат в браузере
5. Меняешь код
6. Браузер обновляется автоматически (HMR)
```

### День 2: Делаешь запрос к API

```javascript
import { useEffect, useState } from 'react'
import api from '@/api/client'

export default function MyComponent() {
  const [data, setData] = useState([])

  useEffect(() => {
    api.get('/users')
      .then(res => setData(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div>
      {data.map(user => <div key={user.id}>{user.name}</div>)}
    </div>
  )
}
```

**Как это работает:**
1. При загрузке компонента - useEffect запускается
2. Делает GET запрос к `/users` на backend
3. Backend отвечает с данными
4. setData обновляет состояние
5. Компонент перерендерится с новыми данными

### День 3: Добавляешь авторизацию

```javascript
import useAuthStore from '@/store/useAuthStore'

export default function LoginButton() {
  const { login, user } = useAuthStore()

  const handleLogin = async (email, password) => {
    const result = await login(email, password)
    if (result) {
      // Успешно залогинились
      navigate('/chat')
    }
  }

  return (
    <button onClick={() => handleLogin('test@test.com', 'pass')}>
      Войти
    </button>
  )
}
```

**Zustand хранилище:**
- Сохраняет состояние пользователя
- Доступно везде через `useAuthStore()`
- Персистент (может сохраняться в localStorage)

---

## 🛠️ Полезные команды

```bash
# Локальная разработка
npm run dev          # Запуск dev сервера на localhost:5173

# Проверка кода
npm run lint         # Проверить синтаксис

# Сборка для production
npm run build        # Собирает в /dist

# Просмотр собранного приложения
npm run preview      # Показывает /dist локально
```

---

## 📚 Используемые библиотеки

| Библиотека | Зачем |
|---|---|
| **react** | UI фреймворк - основа приложения |
| **react-dom** | Рендеринг React в браузер |
| **react-router-dom** | Маршрутизация - переходы между страницами |
| **axios** | HTTP клиент - запросы к API |
| **zustand** | State management - хранилище состояния |
| **tailwindcss** | CSS фреймворк - классы для стилизации |
| **vite** | Бандлер - сборка и оптимизация |
| **eslint** | Проверка кода на ошибки |

---

## 💡 Для собеседования

> "Я использую React с Vite для быстрой разработки. 
> Приложение использует react-router-dom для маршрутизации между страницами,
> zustand для управления состоянием авторизации, и axios для запросов к API.
> При разработке запускаю npm run dev с HMR (горячей перезагрузкой),
> а при развертывании собираю в статические файлы через npm run build
> и раздаю через nginx в Docker контейнере."

---

## 🎯 Что дальше?

1. **Запусти локально:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Откройся в браузере:** `http://localhost:5173`

3. **Посмотри структуру:** `src/pages/`, `src/components/`

4. **Изучи как работает API:** `src/api/client.js` (если есть)

5. **Найди useAuthStore:** `src/store/useAuthStore.js` - вся логика авторизации


FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости для ML
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY app/settings/requirements.ml.txt .
RUN pip install --no-cache-dir -r requirements.ml.txt

# Копируем ML код
COPY app/ml/ ./ml/
COPY app/ml_service.py .

# Создаем пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "ml_service:app", "--host", "0.0.0.0", "--port", "8001"]
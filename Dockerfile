FROM python:3.12-slim

WORKDIR /app

COPY app/settings/requirements.base.txt .
COPY app/settings/requirements.prod.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ARG ENVIRONMENT=development
RUN if [ "$ENVIRONMENT" = "development" ]; then \
      pip install --no-cache-dir -r requirements.dev.txt; \
    fi

COPY app/ .


RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
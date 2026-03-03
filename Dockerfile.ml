FROM python:3.9-slim

WORKDIR /app

COPY requirements.ml.txt .
RUN pip install --no-cache-dir -r requirements.ml.txt

COPY app/ml_service.py .
COPY app/ml/ ./ml/

CMD ["uvicorn", "ml_service:app", "--host", "0.0.0.0", "--port", "8001"]
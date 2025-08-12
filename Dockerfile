FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .


RUN pip install -r settings\requirements.txt --no-cache-dir --upgrade



COPY . .

# Expose the port
EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
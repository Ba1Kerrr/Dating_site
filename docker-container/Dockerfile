FROM python:3.12-slim

WORKDIR /app

COPY app/settings/requirements.txt .

ENV PYTHONDWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt --no-cache-dir --upgrade


COPY ./app app


# Expose the port
EXPOSE 8000


CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
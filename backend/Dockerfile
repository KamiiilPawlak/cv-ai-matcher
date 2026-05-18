FROM python:3.11-slim

# 1. Ustawienia środowiskowe Pythona
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code


RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-pol \
    libmagic1 \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml .


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[dev]


COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
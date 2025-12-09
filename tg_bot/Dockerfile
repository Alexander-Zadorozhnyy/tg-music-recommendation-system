FROM python:3.12-slim

WORKDIR /tg_bot

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && pip install psycopg2-binary \
    && pip install python-multipart \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos "" appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

COPY . .

VOLUME /app/data

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "main"]

FROM python:3.11-slim

WORKDIR /app

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

CMD ["python", "-m", "app.main"]

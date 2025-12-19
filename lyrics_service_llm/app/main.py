import json
import pika
import os
import time
from dotenv import load_dotenv

from app.repo_csv import CsvLyricsRepository
from app.processor import process_message
from app.rabbit_producer import send_result_message

load_dotenv()

def getenv_any(*names, default=None):
    for n in names:
        v = os.getenv(n)
        if v not in (None, ""):
            return v
    return default

CSV_PATH    = getenv_any("CSV_PATH", default="/data/songs.csv")
RABBIT_HOST = getenv_any("RABBIT_HOST", "RABBITMQ_HOST", default="rabbitmq")
RABBIT_PORT = int(getenv_any("RABBIT_PORT", "RABBITMQ_PORT", default="5672"))
QUEUE_IN    = getenv_any("QUEUE_IN", default="fetch_lyrics")

repo = CsvLyricsRepository(CSV_PATH)

def on_message(ch, method, properties, body):
    print("[main] Received message")
    msg = json.loads(body)
    result = process_message(msg, repo)
    send_result_message(result)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    while True:
        try:
            print("[main] Connecting to RabbitMQ...")
            params = pika.ConnectionParameters(
                host=RABBIT_HOST,
                port=RABBIT_PORT,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            connection = pika.BlockingConnection(params)
            break
        except pika.exceptions.AMQPConnectionError:
            print("[main] RabbitMQ not ready, retrying in 3s...")
            time.sleep(3)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_IN, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_IN, on_message_callback=on_message)

    print(f"[main] Waiting for messages in '{QUEUE_IN}'")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()

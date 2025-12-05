import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


def getenv_any(*names, default=None):
    for n in names:
        v = os.getenv(n)
        if v not in (None, ""):
            return v
    return default


RABBIT_HOST = getenv_any("RABBIT_HOST", "RABBITMQ_HOST", default="rabbitmq")
RABBIT_PORT = int(getenv_any("RABBIT_PORT", "RABBITMQ_PORT", default="5672"))
QUEUE_OUT = getenv_any(
    "QUEUE_OUT", default="lyrics_responses"
)  # дефолт на случай опечатки в compose


def send_result_message(message: dict):
    params = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_OUT, durable=True)
    channel.basic_publish(exchange="", routing_key=QUEUE_OUT, body=json.dumps(message))
    connection.close()
    print(f"[producer] Sent to {QUEUE_OUT}: {message.get('id')}")

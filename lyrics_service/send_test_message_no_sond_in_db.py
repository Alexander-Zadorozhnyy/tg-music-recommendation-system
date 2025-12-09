# send_test_message_no_sond_in_db.py

import pika
import json

RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
QUEUE_IN = "fetch_lyrics"

message = {
    "id": "req_no_csv",
    "user_id": "user99",
    "song_credits": [{"artist": "adele", "song": "hello"}],  # заведомо отсутствует
    "query": "что-то красивое",
}

connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT)
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_IN, durable=True)
channel.basic_publish(exchange="", routing_key=QUEUE_IN, body=json.dumps(message))
connection.close()

print(f"[test] Sent test message to {QUEUE_IN}")

# send_test_message.py
import pika
import json

# параметры подключения к RabbitMQ на твоей машине
RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
QUEUE_IN = "fetch_lyrics"

# сообщение, которое точно найдётся в твоём CSV (radiohead - vegetable)
message = {
    "id": "req1",
    "user_id": "user42",
    "song_credits": [
        {"artist": "radiohead", "track": "vegetable"}
    ],
    "query": "что-то грустное"
}

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_IN, durable=True)
channel.basic_publish(exchange="", routing_key=QUEUE_IN, body=json.dumps(message))
connection.close()

print(f"[test] Sent test message to {QUEUE_IN}")

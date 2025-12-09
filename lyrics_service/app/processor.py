import asyncio
import json
import logging

import aio_pika

from app.models import IncomingMessage, OutgoingMessage, SongText
from app.repo_csv import CsvLyricsRepository
from app.lyrics_api import fetch_lyrics_from_api
from app.text_compressor import extract_keywords

from rabbitmq.aio_client import RobustRabbitMQClient


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RequestProcessor:
    def __init__(self, host, port, requests_queue, destination_queue, csv_path):
        self.rabbitmq_client = RobustRabbitMQClient(host, port)

        self.requests_queue = requests_queue
        self.destination_queue = destination_queue

        self.repo = CsvLyricsRepository(csv_path)
        self._process_task = None

    def start(self):
        if not self._process_task:
            asyncio.create_task(self.loop())

    async def loop(self):
        logging.info("Starting loop...")
        await self.rabbitmq_client.consume_messages(
            self.requests_queue, self.process_message_callback
        )

    async def process_message_callback(self, message: aio_pika.IncomingMessage):
        """
        Main callback that processes incoming messages.
        """

        try:
            # Parse the message
            body = message.body.decode("utf-8")
            data = json.loads(body)

            logging.info(f"Processing message: {data.get('type', 'unknown')}")

            processed_data = await self.process_single_request(data)
            logging.info(f"Processed data: {processed_data}")

            # Send to destination queue
            success = await self.forward_to_destination(processed_data)

            if success:
                # Acknowledge the message
                await message.ack()
                logging.info("Successfully processed message")
            else:
                # Negative acknowledge - requeue for retry
                await message.nack(requeue=True)
                logging.warning("Failed to forward message, requeuing")

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON: {e}")
            await message.reject(requeue=False)  # Don't requeue invalid messages

        except KeyError as e:
            logging.error(f"Missing required field {e} in message")
            await message.nack(requeue=False)  # Send to DLQ

        except Exception as e:
            logging.error(f"Unexpected error processing message: {e}")
            await message.nack(requeue=True)  # Requeue for retr

    async def process_single_request(self, msg: IncomingMessage) -> OutgoingMessage:
        results: list[SongText] = []

        for credit in msg["song_credits"]:
            artist = credit["artist"]
            song = credit["song"]

            lyrics = self.repo.find_lyrics(artist, song)
            if not lyrics:
                lyrics = fetch_lyrics_from_api(artist, song)

            keywords = extract_keywords(lyrics)

            results.append(
                {"artist": artist, "song": song, "lyrics": lyrics, "keywords": keywords}
            )

        return {
            "id": msg["id"],
            "user_id": msg["user_id"],
            "query": msg["query"],
            "songs_texts": results,
        }

    async def forward_to_destination(self, data: OutgoingMessage) -> bool:
        """
        Forward processed data to destination queue.
        """
        try:
            message_body = json.dumps(data, ensure_ascii=False)

            # Use the client's publish method
            await self.rabbitmq_client.publish_message(
                queue_name=self.destination_queue, body=message_body
            )

            return True

        except Exception as e:
            logging.error(f"Failed to forward to destination: {e}")
            return False

    def stop(self):
        if self._process_task:
            self._process_task.cancel()

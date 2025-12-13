import asyncio
import json
import logging
from typing import Any

import aio_pika
import httpx

from src.models import IncomingMessage, OutgoingMessage, ResponseTrack, SongText

from rabbitmq.aio_client import RobustRabbitMQClient


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LyricsProcessor:
    def __init__(
        self, host, port, requests_queue, destination_queue, opensearch_service_url
    ):
        self.rabbitmq_client = RobustRabbitMQClient(host, port)

        self.requests_queue = requests_queue
        self.destination_queue = destination_queue

        self.opensearch_service_url = opensearch_service_url

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

            # logging.info(f"Processing message: {data=}")

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

    async def process_single_request(
        self, msg: IncomingMessage
    ) -> OutgoingMessage:  # TODO: Replace with actual recommendation system
        request = " | ".join([self.process_single_track(x) for x in msg["songs_texts"]])
        response = f"Cannot find recommendations for such request: {request}"
        try:
            async with httpx.AsyncClient() as client:
                url = self.opensearch_service_url + "/search"

                post_response = await client.post(
                    url,
                    timeout=5,  # Set appropriate timeout
                    json={
                        "query": request,
                        "size": 5,
                    },
                )
                post_response.raise_for_status()
                parsed_response = post_response.json()
                print(f"{parsed_response=}")
                response = (
                    "🎶 На основе вашего запроса подобрали следующие композиции:\n\n```md\n"
                    + "\n".join(
                        [
                            self.process_single_response_track(i, x)
                            for i, x in enumerate(parsed_response["results"])
                        ]
                    )
                    + "```"
                )

        except Exception as e:
            logging.error(
                f"Cannot find recommendations for such request: {request}. Error: {e}"
            )

        return {
            "id": msg["id"],
            "user_id": msg["user_id"],
            "response": response,
        }

    def process_single_track(self, text: SongText):
        return f"{text['artist']}:{text['song']} - {', '.join(text['keywords'])}"

    def process_single_response_track(self, num: int, response_track: ResponseTrack):
        return f"📀 {num}) {response_track['artist_name']} - {response_track['track_name']} ({response_track['release_date']}). Score: {response_track['score']}"

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


# eminem - Lose Yourself
# eminem - Stan
# eminem - Rap God

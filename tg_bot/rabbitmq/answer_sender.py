import asyncio
import json
import logging

import aio_pika


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MessageSender:
    def __init__(
        self,
        bot,
        rabbitmq_client,
        response_queue,
    ):
        self.bot = bot
        self.rabbitmq_client = rabbitmq_client

        self.response_queue = response_queue

        self._process_task = None

    def start(self):
        if not self._process_task:
            asyncio.create_task(self.loop())

    async def loop(self):
        logging.info("Starting loop...")
        await self.rabbitmq_client.consume_messages(
            self.response_queue, self.process_message_callback
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

            await self.bot.send_message(
                chat_id=767149056, text=data["response"]
            )  # TODO: get real id from db

            if True:
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

    def stop(self):
        if self._process_task:
            self._process_task.cancel()


# eminem - Lose Yourself
# eminem - Stan
# eminem - Rap God

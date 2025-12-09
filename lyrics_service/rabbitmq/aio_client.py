import asyncio
import logging
from typing import Callable, Awaitable, Optional

import aio_pika
from aio_pika import exceptions as ap_exc

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RobustRabbitMQClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        heartbeat: int = 600,
    ):
        self.host = host
        self.port = port
        self.heartbeat = heartbeat

        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.is_connected: bool = False

    async def connect(self) -> bool:
        """Async connect with retry + exponential backoff"""

        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                logging.info(
                    f"Connecting to RabbitMQ {self.host}:{self.port} (attempt={attempt + 1})"
                )

                self.connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=self.port,
                    heartbeat=self.heartbeat,
                )  # type: ignore

                self.channel = await self.connection.channel()  # type: ignore
                await self.channel.set_qos(prefetch_count=1)  # type: ignore

                self.is_connected = True
                logging.info("Successfully connected to RabbitMQ")

                return True

            except Exception as e:
                logging.error(f"Connection attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # exponential backoff
                else:
                    logging.error("All connection attempts failed")
                    return False

        return False

    async def ensure_connection(self) -> bool:
        """Reconnect automatically if the connection is lost"""
        if not self.is_connected or self.connection.is_closed:
            logging.warning("RabbitMQ connection lost, reconnecting...")
            return await self.connect()
        return True

    async def publish_message(self, queue_name: str, body: str):
        """Publish message with reconnection & retry"""

        for _ in range(3):
            try:
                if not await self.ensure_connection():
                    logging.error("Cannot re-establish connection")
                    await asyncio.sleep(3)

                # ensure queue exists
                await self.channel.declare_queue(
                    queue_name,
                    durable=True,
                )

                await self.channel.default_exchange.publish(
                    aio_pika.Message(body=body.encode()),
                    routing_key=queue_name,
                )
                return

            except (
                ap_exc.ConnectionClosed,
                ap_exc.ChannelClosed,
                ap_exc.AMQPConnectionError,
            ) as e:
                logging.error(f"Publish failed (connection lost): {e}, retrying...")
                self.is_connected = False

            except Exception as e:
                logging.error(f"Unexpected publish error: {e}")

        logging.error("Failed to publish message after retries.")

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable[[aio_pika.IncomingMessage], Awaitable[None]],
    ):
        """
        Start consuming messages, automatically reconnect if connection lost.
        """

        while True:
            try:
                if not await self.ensure_connection():
                    logging.error("Cannot establish connection to RabbitMQ, waiting...")
                    await asyncio.sleep(2)
                    continue

                queue = await self.channel.declare_queue(
                    queue_name,
                    durable=True,
                )

                logging.info(f"Started consuming from queue: {queue_name}")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        try:
                            await callback(message)
                        except Exception as e:
                            logging.error(f"Callback error: {e}")
                            await message.nack(requeue=True)

            except (
                ap_exc.ConnectionClosed,
                ap_exc.ChannelClosed,
                ap_exc.AMQPConnectionError,
            ) as e:
                logging.error(
                    f"RabbitMQ connection lost in consumer: {e}, reconnecting..."
                )
                self.is_connected = False
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                logging.info("Consumer task cancelled gracefully")
                return

            except Exception as e:
                logging.error(f"Unexpected consumer error: {e}")
                self.is_connected = False
                await asyncio.sleep(10)

    async def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logging.info("RabbitMQ connection closed")
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


if __name__ == "__main__":

    async def test():
        rabbitmq_client = RobustRabbitMQClient("localhost", 5672)

        await rabbitmq_client.connect()

        async def sample_callback(message: aio_pika.IncomingMessage):
            print("Received message:", message.body.decode())
            await message.ack()

        # Start consuming in background
        asyncio.create_task(
            rabbitmq_client.consume_messages("requests", sample_callback)
        )

        # Publish a test message
        for _ in range(5):
            # await client.publish_message("test_queue", "Hello, RabbitMQ!")
            await asyncio.sleep(10)

        await rabbitmq_client.close()

    asyncio.run(test())

import asyncio
import json
import logging

import aio_pika

from database.config import get_settings

settings = get_settings()


from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from models.request import Request
from models.user import User
from models.response import Response

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MessageSender:
    def __init__(self, bot, rabbitmq_client):
        self.bot = bot
        self.rabbitmq_client = rabbitmq_client

        self.response_queue = settings.QUEUE_RESPONSE

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
        try:
            body = message.body.decode("utf-8")
            data = json.loads(body)

            request_id = data.get("request_id")
            response_text = data.get("response")

            if not request_id or response_text is None:
                raise KeyError("request_id or response")

            # Получаем сессию и данные из БД
            async with get_session() as session:
                # Получаем запрос
                request = await session.get(Request, request_id)
                if not request:
                    logging.error(f"Request {request_id} not found")
                    await message.nack(requeue=False)
                    return

                # Получаем пользователя
                user = await session.get(User, request.user_id)
                if not user or not user.telegram_id:
                    logging.error(f"User {request.user_id} missing telegram_id")
                    await message.nack(requeue=False)
                    return

                telegram_chat_id = int(user.telegram_id)

                # Отправляем сообщение
                await self.bot.send_message(
                    chat_id=telegram_chat_id,
                    text=response_text,
                    parse_mode="MarkdownV2",
                )

                # Сохраняем ответ в БД
                new_response = Response(
                    user_id=request.user_id,
                    request_id=request_id,
                    response_text=response_text,
                )
                session.add(new_response)
                await session.commit()

            # Подтверждаем обработку
            await message.ack()
            logging.info(
                f"Successfully processed request {request_id} for user {telegram_chat_id}"
            )

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON: {e}")
            await message.reject(requeue=False)

        except KeyError as e:
            logging.error(f"Missing field: {e}")
            await message.nack(requeue=False)

        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            await message.nack(requeue=True)

    def stop(self):
        if self._process_task:
            self._process_task.cancel()


# eminem - Lose Yourself
# eminem - Stan
# eminem - Rap God

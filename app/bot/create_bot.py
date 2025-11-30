from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

last_bot_messages: dict[int, str] = {}


_original_send_message = bot.send_message


async def capture_send_message(chat_id, text, *args, **kwargs):
    last_bot_messages[chat_id] = text
    return await _original_send_message(chat_id, text, *args, **kwargs)


bot.send_message = capture_send_message


async def start_bot():
    try:
        await bot.send_message(settings.ADMIN_ID, "Я запущен 🥳.")
    except:
        pass


async def stop_bot():
    try:
        await bot.send_message(settings.ADMIN_ID, "Бот остановлен 😔.")
    except:
        pass

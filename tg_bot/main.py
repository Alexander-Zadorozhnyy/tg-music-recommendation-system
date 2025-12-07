import asyncio
import logging
from models import User, Request, Response
from bot.create_bot import dp, stop_bot, start_bot, bot
from bot.handlers import recommendation_router, user_router
from database.database import init_db

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    try:
        logging.info("Initializing database...")
        await init_db(drop_all=False)

        logging.info("Starting bot setup...")
        dp.include_router(user_router)
        dp.include_router(recommendation_router)
        await start_bot()

        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        logging.info("Shutting down bot...")
        await stop_bot()


if __name__ == "__main__":
    asyncio.run(main())

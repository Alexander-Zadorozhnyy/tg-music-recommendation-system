import asyncio
import logging

from app.bot.create_bot import dp, stop_bot, start_bot, bot
from app.bot.handlers import recommendation_router, user_router

from app.db import async_main

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    try:
        logging.info("Starting bot setup...")
        dp.include_router(user_router)
        dp.include_router(recommendation_router)
        await async_main()
        await start_bot()

        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        logging.info("Shutting down bot...")
        await stop_bot()


if __name__ == "__main__":
    asyncio.run(main())

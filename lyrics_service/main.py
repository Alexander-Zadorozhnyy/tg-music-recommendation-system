import asyncio
import logging
import os
import sys

sys.path.insert(0, os.getcwd())

from config import get_settings
from src.request_processor import RequestProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

settings = get_settings()


async def start_worker():
    try:
        processor = RequestProcessor(
            host=settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            requests_queue=settings.QUEUE_IN,
            destination_queue=settings.QUEUE_OUT,
            csv_path=settings.CSV_PATH,
            genius_token=settings.GENIUS_API_TOKEN,
        )
        processor.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stop lyrics processing")
        processor.stop()


if __name__ == "__main__":
    asyncio.run(start_worker())

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.getcwd())

from config import get_settings
from src.lyrics_processor import LyricsProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

settings = get_settings()


async def start_worker():
    try:
        processor = LyricsProcessor(
            host=settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            requests_queue=settings.QUEUE_IN,
            destination_queue=settings.QUEUE_OUT,
            opensearch_service_url=settings.OPENSEARH_SERVICE_URL,
        )
        processor.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stop lyrics processing")
        processor.stop()


if __name__ == "__main__":
    asyncio.run(start_worker())

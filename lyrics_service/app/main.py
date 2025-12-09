import asyncio
import logging
import os
from dotenv import load_dotenv

from app.processor import RequestProcessor

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def getenv_any(*names, default=None):
    for n in names:
        v = os.getenv(n)
        if v not in (None, ""):
            return v
    return default


CSV_PATH = getenv_any("CSV_PATH", default="/data/songs.csv")
RABBIT_HOST = getenv_any("RABBIT_HOST", "RABBITMQ_HOST", default="rabbitmq")
RABBIT_PORT = int(getenv_any("RABBIT_PORT", "RABBITMQ_PORT", default="5672"))
QUEUE_IN = getenv_any("QUEUE_IN", default="fetch_lyrics")
QUEUE_OUT = getenv_any("QUEUE_OUT", default="lyrics_responses")


async def start_worker():
    try:
        processor = RequestProcessor(
            RABBIT_HOST, RABBIT_PORT, QUEUE_IN, QUEUE_OUT, CSV_PATH
        )
        processor.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stop lyrics processing")
        processor.stop()


if __name__ == "__main__":
    asyncio.run(start_worker())

import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    GENIUS_API_TOKEN: Optional[str] = os.getenv("GENIUS_API_TOKEN", None)

    RABBIT_HOST: str = os.getenv("RABBIT_HOST", "rabbitmq")
    RABBIT_PORT: int = int(os.getenv("RABBIT_PORT", 5432))
    RABBIT_USER: str = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASS: str = os.getenv("RABBIT_PASS", "guest")

    QUEUE_IN: str = os.getenv("QUEUE_REQUESTS", "requests")
    QUEUE_OUT: str = os.getenv("QUEUE_LYRICS", "lyrics")

    CSV_PATH: str = "./data/songs.csv"

    def validate(self) -> None:
        if self.GENIUS_API_TOKEN is None:
            raise ValueError("GENIUS_API_TOKEN is required")

        if not all(
            [self.RABBIT_HOST, self.RABBIT_PORT, self.RABBIT_USER, self.RABBIT_PASS]
        ):
            raise ValueError("Missing required rabbitmq configuration")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings

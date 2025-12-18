import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    RABBIT_HOST: str = os.getenv("RABBIT_HOST", "rabbitmq")
    RABBIT_PORT: int = int(os.getenv("RABBIT_PORT", 5432))
    RABBIT_USER: str = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASS: str = os.getenv("RABBIT_PASS", "guest")

    QUEUE_IN: str = os.getenv("QUEUE_LYRICS", "lyrics")
    QUEUE_OUT: str = os.getenv("QUEUE_RESPONSE", "response")

    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY", None)
    OPENSEARH_SERVICE_URL: str = os.getenv(
        "OPENSEARCH_SERVICE_URL", "http://opensearch_service:8009"
    )

    def validate(self) -> None:
        if not all(
            [self.RABBIT_HOST, self.RABBIT_PORT, self.RABBIT_USER, self.RABBIT_PASS]
        ):
            raise ValueError("Missing required rabbitmq configuration")

        if not self.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is required")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings

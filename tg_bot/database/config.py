import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN", None)
    ADMIN_ID: Optional[int] = (
        int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") is not None else None
    )

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")

    RABBIT_HOST: str = os.getenv("RABBIT_HOST", "rabbitmq")
    RABBIT_PORT: int = int(os.getenv("RABBIT_PORT", 5432))
    RABBIT_USER: str = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASS: str = os.getenv("RABBIT_PASS", "guest")

    QUEUE_RESPONSE: str = os.getenv("QUEUE_RESPONSE", "response")

    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY", None)

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def validate(self) -> None:
        if not all(
            [
                self.POSTGRES_HOST,
                self.POSTGRES_DB,
                self.POSTGRES_PASSWORD,
                self.POSTGRES_USER,
            ]
        ):
            raise ValueError("Missing required database configuration")
        if not all(
            [self.RABBIT_HOST, self.RABBIT_PORT, self.RABBIT_USER, self.RABBIT_PASS]
        ):
            raise ValueError("Missing required rabbitmq configuration")
        if not self.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is required")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if self.ADMIN_ID is None:
            raise ValueError("ADMIN_ID must be an integer")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    GENIUS_API_TOKEN: str

    RABBIT_HOST: str = "rabbitmq"
    RABBIT_PORT: int = 5672
    RABBIT_USER: Optional[str] = None
    RABBIT_PASS: Optional[str] = None

    QUEUE_IN: str = "requests"
    QUEUE_OUT: str = "lyrics"

    CSV_PATH: str = "./data/songs.csv"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

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

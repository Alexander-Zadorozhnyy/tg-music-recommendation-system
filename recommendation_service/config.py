from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    RABBIT_HOST: str = "rabbitmq"
    RABBIT_PORT: int = 5672
    RABBIT_USER: Optional[str] = None
    RABBIT_PASS: Optional[str] = None

    QUEUE_IN: str = "lyrics"
    QUEUE_OUT: str = "response"

    MISTRAL_API_KEY: Optional[str] = None
    OPENSEARH_SERVICE_URL: str = "http://localhost:8009"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
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

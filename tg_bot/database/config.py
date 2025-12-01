from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):

    BOT_TOKEN: Optional[str] = None
    ADMIN_ID: int

    DB_HOST: Optional[str] = None
    DB_PORT: int
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    MISTRAL_API_KEY: Optional[str] = None

    @property
    def DATABASE_URL(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore" 
    )

    def validate(self) -> None:
        if not all([self.DB_HOST, self.DB_NAME, self.DB_PASS, self.DB_USER]):
            raise ValueError("Missing required database configuration")
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
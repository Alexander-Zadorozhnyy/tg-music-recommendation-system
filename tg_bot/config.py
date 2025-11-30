import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    PG_DATABASE: str
    PG_DEFAULT_DATABASE: str
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )


settings = Settings()

"""Конфигурация приложения."""

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.getcwd(), ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Settings:
    """Настройки приложения."""

    OPENSEARCH_URL: str = os.getenv("OPENSEARCH_URL", "https://localhost:9200")
    OPENSEARCH_USER: str = os.getenv("OPENSEARCH_USER", "")
    OPENSEARCH_INITIAL_ADMIN_PASSWORD: str = os.getenv(
        "OPENSEARCH_INITIAL_ADMIN_PASSWORD", ""
    )
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    YANDEX_FOLDER_ID: str = os.getenv("YANDEX_FOLDER_ID", "")
    YANDEX_EMBED_MODEL: str = os.getenv("YANDEX_EMBED_MODEL", "text-search-doc")
    YANDEX_EMBEDDINGS_URL: str = os.getenv(
        "YANDEX_EMBEDDINGS_URL",
        "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding",
    )
    INDEX_NAME: str = os.getenv("OPENSEARCH_INDEX", "music_ceds_semantic")
    CSV_FILE: str = os.getenv("CSV_FILE", "./data/tcc_ceds_music.csv")
    APP_NAME: str = "Music Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    def validate(self) -> None:
        """Проверяет, что все обязательные настройки заполнены."""
        errors = []

        if not self.OPENSEARCH_USER:
            errors.append(
                "OPENSEARCH_USER не установлен. Установите через переменную окружения или .env файл"
            )
        if not self.OPENSEARCH_INITIAL_ADMIN_PASSWORD:
            errors.append(
                "OPENSEARCH_INITIAL_ADMIN_PASSWORD не установлен. Установите через переменную окружения или .env файл"
            )
        if not self.YANDEX_API_KEY:
            errors.append(
                "YANDEX_API_KEY не установлен. Установите через переменную окружения или .env файл"
            )
        if not self.YANDEX_FOLDER_ID:
            errors.append(
                "YANDEX_FOLDER_ID не установлен. Установите через переменную окружения или .env файл"
            )

        if errors:
            error_msg = "\n".join(f"  - {error}" for error in errors)
            raise ValueError(
                f"Обязательные настройки не заполнены:\n{error_msg}\n\n"
                "Создайте файл .env или установите переменные окружения.\n"
                "См. env.example для примера."
            )


settings = Settings()

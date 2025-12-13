"""Главный файл FastAPI приложения."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from app.routers import search, health

dotenv_path = os.path.join(os.getcwd(), ".env")
print(dotenv_path)

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

try:
    settings.validate()
except ValueError as e:
    import sys

    print(f"ОШИБКА КОНФИГУРАЦИИ: {e}", file=sys.stderr)
    sys.exit(1)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API для поиска по музыкальному индексу CEDS",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(health.router)


@app.get("/", tags=["root"])
async def root():
    """Корневой endpoint."""
    return {
        "message": "Music Search API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

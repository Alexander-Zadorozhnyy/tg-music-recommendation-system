import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from app.config import settings


def create_database():
    DATABASE_URL = f"postgresql://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DEFAULT_DATABASE}"
    default_engine = create_engine(
        DATABASE_URL,
        isolation_level="AUTOCOMMIT",
    )

    with default_engine.connect() as conn:
        datname = settings.PG_DATABASE
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{datname}'")
        )
        exists = result.scalar() is not None

        if not exists:
            conn.execute(text(f'CREATE DATABASE "{datname}"'))
            print(f"Database '{datname}' created.")
        else:
            print(f"Database '{datname}' already exists.")


# engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
create_database()
DATABASE_URL = f"postgresql+asyncpg://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DATABASE}"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
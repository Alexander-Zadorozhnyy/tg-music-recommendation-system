from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from models.user import User
from sqlmodel import select
import bot.keyboards as kb
import logging
from database.database import AsyncSessionLocal

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    async with AsyncSessionLocal() as session:
        result = await session.exec(select(User).where(User.telegram_id == user_id))
        user = result.first()

        if not user:
            user = User(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logging.info(f"✅ Created user {user_id}")
        else:
            logging.info(f"✅ User {user_id} already exists")

    await message.answer("🎵 Добро пожаловать...", reply_markup=kb.menu)

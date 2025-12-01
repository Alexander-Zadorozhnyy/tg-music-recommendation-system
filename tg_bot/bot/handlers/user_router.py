from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from models import User
from sqlmodel import select
import bot.keyboards as kb
import logging
from database.database import get_db_session


user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    session = get_db_session()
    try:
        result = await session.exec(select(User).where(User.telegram_id == user_id))
        user = result.first()

        if not user:
            user = User(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logging.info(f"✅ Created user {user_id}")
        else:
            logging.info(f"✅ User {user_id} already exists")

    finally:
        await session.close()

    await message.answer("🎵 Добро пожаловать в музыкального помощника!", reply_markup=kb.menu)

    

@user_router.message(F.text == "Моя музыкальная статистика 📊")
async def music_statistics(message: Message):
    try:
        # TODO: здесь тоже нужно будет использовать асинхронный запрос через get_session()
        stats = {
            "total_tracks": 5,
            "top_genre": "rap",
            "top_artist": "Eminem",
            "activity_level": "2 дня подряд",
        }
        await message.answer(
            f"📊 Ваша музыкальная статистика:\n\n"
            f"🎵 Всего подобрано треков: {stats['total_tracks']}\n"
            f"🎸 Любимый жанр: {stats['top_genre']}\n"
            f"👑 Топ-исполнитель: {stats['top_artist']}\n"
            f"📅 Активность: {stats['activity_level']}"
        )
    except Exception as e:
        logging.error(f"Error loading stats: {e}")
        await message.answer("❌ Не удалось загрузить статистику.")


@user_router.message(F.text == "Назад ◀️")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=kb.menu)
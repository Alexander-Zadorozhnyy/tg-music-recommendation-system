from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import app.db.requests as rq
import app.bot.keyboards as kb

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(
        "🎵 Добро пожаловать в MelodyMate!\n\n"
        "Ваш интеллектуальный помощник для поиска идеальной музыки. "
        "Я использую современные алгоритмы ML и NLP, чтобы подобрать треки, "
        "которые точно понравятся именно вам!",
        reply_markup=kb.menu,
    )


@user_router.message(F.text == "Моя музыкальная статистика 📊")
async def music_statistics(message: Message):
    try:
        stats = {
            "total_tracks": 5,
            "top_genre": "rap",
            "top_artist": "Eminem",
            "activity_level": "2 дня подряд",
        }  # TODO: await rq.get_user_statistics(message.from_user.id)
        await message.answer(
            f"📊 Ваша музыкальная статистика:\n\n"
            f"🎵 Всего подобрано треков: {stats['total_tracks']}\n"
            f"🎸 Любимый жанр: {stats['top_genre']}\n"
            f"👑 Топ-исполнитель: {stats['top_artist']}\n"
            f"📅 Активность: {stats['activity_level']}"
        )
    except Exception as e:
        await message.answer("❌ Не удалось загрузить статистику.")
        
        
@user_router.message(F.text == "Назад ◀️")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=kb.menu)
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти рекомендации 🎧")],
        [KeyboardButton(text="Моя музыкальная статистика 📊")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)


async def recommendation_methods():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рекомендации по истории 🕒")],
            [KeyboardButton(text="Подобрать похожие 🎵")],
            [KeyboardButton(text="Свободный запрос 💬")],
            [KeyboardButton(text="Назад ◀️")],
        ],
        resize_keyboard=True,
    )

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.bot.states.bot_state import RecommendationStates
from app.bot.utils.utils import (
    get_response_based_on_free_form_request,
    get_response_based_on_similar_tracks,
    smart_parse_tracks_input,
)
import app.db.requests as rq
import app.bot.keyboards as kb

recommendation_router = Router()


@recommendation_router.message(F.text == "Найти рекомендации 🎧")
async def find_recommendations(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎶 Выберите способ получения рекомендаций:",
        reply_markup=await kb.recommendation_methods(),
    )


@recommendation_router.message(F.text == "Рекомендации по истории 🕒")
async def recommendations_by_history(message: Message):
    # Получаем рекомендации на основе истории прослушиваний
    try:
        recommendations = [
            "Post Malone - Rockstar",
            "Eminem - Rap God",
        ]  # TODO, get based on history await rq.get_recommendations_by_history(message.from_user.id)
        if recommendations:
            response = "🎵 Ваши персонализированные рекомендации:\n\n"
            for i, track in enumerate(recommendations[:10], 1):
                response += f"{i}. {track}\n"
            await message.answer(response)
        else:
            await message.answer(
                "📝 У вас пока недостаточно истории прослушиваний.\n"
                "Попробуйте другие методы рекомендаций или оцените несколько треков!"
            )
    except Exception:
        await message.answer(
            "❌ Произошла ошибка при получении рекомендаций. Попробуйте позже."
        )


@recommendation_router.message(F.text == "Подобрать похожие 🎵")
async def find_similar_tracks(message: Message, state: FSMContext):
    await state.set_state(RecommendationStates.waiting_tracks_input)
    await message.answer(
        "🎵 Введите треки, на основе которых подобрать похожие:\n\n"
        "💡 Формат: каждый трек с новой строки\n"
        "📝 Пример:\n"
        "<code>The Weeknd - Blinding Lights\n"
        "Daft Punk - Get Lucky\n"
        "Arctic Monkeys - Do I Wanna Know?\n"
        "Lana Del Rey - Summertime Sadness\n"
        "MGMT - Little Dark Age</code>\n\n"
        "Можно ввести от 1 до 10 треков",
        parse_mode="HTML",
    )


@recommendation_router.message(F.text == "Свободный запрос 💬")
async def free_form_recommendation(message: Message, state: FSMContext):
    await state.set_state(RecommendationStates.waiting_free_form)
    await message.answer(
        "💭 Опишите, какую музыку вы хотите найти:\n\n"
        "Примеры запросов:\n"
        '• "Что-то энергичное для тренировки"\n'
        '• "Спокойная музыка для работы"\n'
        '• "Похоже на The Weeknd и Daft Punk"\n'
        '• "Новинки в стиле инди-поп"\n'
        '• "Треки которые слушают программисты"'
    )


@recommendation_router.message(RecommendationStates.waiting_tracks_input)
async def process_tracks_input(message: Message, state: FSMContext):
    user_input = message.text.strip()

    tracks = await smart_parse_tracks_input(user_input)  # TODO: Replace with LLM SO

    if not tracks:
        await message.answer(
            "❌ Не удалось распознать треки. Пожалуйста, введите в формате:\n\n"
            "<code>Исполнитель - Название трека</code>\n"
            "<code>Исполнитель - Название трека</code>",
            parse_mode="HTML",
        )
        return

    if len(tracks) > 10:
        await message.answer("❌ Слишком много треков. Максимум 10.")
        return

    try:
        # Show that processing is underway
        processing_msg = await message.answer("🔍 Ищу похожие треки...")

        # Receive recommendations
        similar_tracks = [
            ["Post Malone", "Rockstar", 30],
            ["Eminem", "Rap God", 35],
        ]  # await rq.get_similar_tracks_by_list(tracks)

        response = get_response_based_on_similar_tracks(tracks, similar_tracks)
        await message.answer(response)
    except Exception as e:
        await message.answer("❌ Произошла ошибка при поиске. Попробуйте позже.")
        import traceback

        traceback.print_exc()
        print(f"Error in similar tracks: {e}")

    finally:
        await state.clear()
        # Deleting the "Processing in progress" message if it has been sent
        try:
            await processing_msg.delete()
        except Exception:
            pass


@recommendation_router.message(RecommendationStates.waiting_free_form)
async def process_free_form_request(message: Message, state: FSMContext):
    user_request = message.text
    try:
        # Используем LLM для обработки свободного запроса
        recommendations = [
            "Post Malone - Rockstar",
            "Eminem - Rap God",
        ]  # TODO: await rq.get_recommendations_by_text(user_request, message.from_user.id)

        response = get_response_based_on_free_form_request(
            user_request, recommendations
        )

        await message.answer(response)
        await state.clear()

    except Exception:
        await message.answer(
            "❌ Не удалось обработать запрос. Попробуйте сформулировать иначе."
        )
        await state.clear()

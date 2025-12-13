import logging
import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.bot_state import RecommendationStates
from bot.utils.utils import (
    get_response_based_on_free_form_request,
    get_response_based_on_similar_tracks,
    smart_parse_tracks_input,
)
import bot.keyboards as kb
from service.llm_connect import LLMService
from models.response import Response
from models.request import Request
from models.user import User
from sqlmodel import select
from database.database import AsyncSessionLocal

from rabbitmq.aio_client import rabbitmq_client
from models.track import TrackItem, TrackList

recommendation_router = Router()


@recommendation_router.message(F.text == "Найти рекомендации 🎧")
async def find_recommendations(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎶 Выберите способ получения рекомендаций:",
        reply_markup=await kb.recommendation_methods(),
    )


@recommendation_router.message(F.text == "Назад ◀️")
async def back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎶 Выберите способ получения рекомендаций:",
        reply_markup=kb.menu,
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
    raw_tracks = await smart_parse_tracks_input(user_input)

    if not raw_tracks:
        await message.answer("❌ Не удалось распознать формат треков.")
        return

    if len(raw_tracks) > 10:
        await message.answer("❌ Максимум 10 треков.")
        return

    try:
        processing_msg = await message.answer("🧹 Исправляю опечатки...")

        normalized = await LLMService.normalize_tracks(raw_tracks)
        # normalized = TrackList(
        #     tracks=[
        #         TrackItem(artist="Arctic Monkeys", song="Do I Wanna Know?"),
        #         TrackItem(artist="Lana Del Rey", song="Summertime Sadness"),
        #         TrackItem(artist="Mgmt", song="Little Dark Age"),
        #     ]
        # )
        logging.info(f"{normalized=}")
        if not normalized.tracks:
            await state.set_state(RecommendationStates.waiting_tracks_input)

            await message.answer(
                "⚠️ Не удалось распознать ни один трек. Проверьте формат:\n"
                "<code>Исполнитель - Название</code>"
                "Попробуйте еще раз!",
                parse_mode="HTML",
                reply_markup=await kb.back_keyboard(),
            )
            return

        diff = len(raw_tracks) - len(normalized.tracks)
        if diff > 0:
            await message.answer(
                f"ℹ️ Исправлено {len(normalized.tracks)} треков. "
                f"{diff} пропущено из-за неясности."
            )

        # Показываем исправленные треки
        response_lines = ["✅ Исправленные треки:"]
        for i, track in enumerate(normalized.tracks, 1):
            response_lines.append(f"{i}. {track.artist} - {track.song}")
        response_lines.append("\n⏳ Скоро появятся рекомендации!")
        response_text = "\n".join(response_lines)

        # 💾 Сохраняем в БД
        async with AsyncSessionLocal() as session:
            result = await session.exec(
                select(User).where(User.telegram_id == str(message.from_user.id))
            )
            user = result.first()
            if not user:
                user = User(
                    telegram_id=str(message.from_user.id),
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

            request = Request(
                user_id=user.id,
                song_credits=json.dumps(
                    [t.dict() for t in normalized.tracks], ensure_ascii=False
                ),
                query="Подбор похожих треков",
            )

            session.add(request)
            await session.commit()

            # response = Response(
            #     user_id=user.id,
            #     request_id=request.id,
            #     response_text=response_text,
            # )
            # session.add(response)
            # await session.commit()

            msg = {
                "id": request.id,
                "user_id": user.id,
                "query": "Подбор похожих треков",
                "song_credits": [t.dict() for t in normalized.tracks],
            }
            await rabbitmq_client.publish_message(
                "requests", json.dumps(msg, ensure_ascii=False)
            )
        await message.answer(response_text)
        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка при нормализации: {e}", exc_info=True)
        await message.answer("❌ Не удалось обработать треки.")
    finally:
        try:
            await processing_msg.delete()
        except Exception:
            pass


@recommendation_router.message(RecommendationStates.waiting_free_form)
async def process_free_form_request(message: Message, state: FSMContext):
    user_request = message.text.strip()

    try:
        is_relevant = await LLMService.is_relevant(user_request)
        if not is_relevant:
            await state.set_state(RecommendationStates.waiting_free_form)
            await message.answer(
                "❌ Этот запрос не связан с музыкой, рекомендациями или исполнителями.\n"
                "Попробуйте описать, какую музыку вы ищете!",
                reply_markup=await kb.back_keyboard(),
            )
            return
    except Exception as e:
        logging.error(f"Ошибка при проверке релевантности: {e}")
        await message.answer("⚠️ Не удалось проверить запрос. Попробуйте позже.")
        await state.clear()
        return

    # Заглушка рекомендаций
    recommendations = [
        "Post Malone - Rockstar",
        "Eminem - Rap God",
        "The Weeknd - Blinding Lights",
    ]
    response_text = get_response_based_on_free_form_request(
        user_request, recommendations
    )

    # Сохраняем в БД
    async with AsyncSessionLocal() as session:
        result = await session.exec(
            select(User).where(User.telegram_id == str(message.from_user.id))
        )
        user = result.first()
        if not user:
            user = User(
                telegram_id=str(message.from_user.id),
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        request = Request(
            user_id=user.id,
            song_credits="",
            query=user_request,
        )
        session.add(request)
        await session.commit()
        await session.refresh(request)

        response = Response(
            user_id=user.id,
            request_id=request.id,
            response_text=response_text,
        )
        session.add(response)
        await session.commit()

    await message.answer(response_text)
    await state.clear()

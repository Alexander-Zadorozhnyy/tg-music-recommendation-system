from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from models.user import User
from sqlmodel import func, select
import bot.keyboards as kb
import logging
from database.database import AsyncSessionLocal
from models.request import Request
from models.response import Response

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


@user_router.message(F.text == "Моя музыкальная статистика 📊")
async def get_music_statistic(message: Message, state: FSMContext):
    stats = await get_enhanced_statistics(message)

    if not stats:
        await message.answer("Статистика не найдена.")
        return

    # Format detailed message
    message_text = "📈 <b>Подробная статистика</b>\n\n"

    message_text += "📊 <b>Общая информация:</b>\n"
    message_text += f"• Всего запросов: {stats['total_requests']}\n"
    message_text += f"• Всего ответов: {stats['total_responses']}\n"
    message_text += f"• Коэффициент ответов: {stats['response_rate']:.1%}\n\n"

    if stats["popular_queries"]:
        message_text += "🔍 <b>Частые запросы:</b>\n"
        for query, count in stats["popular_queries"][:5]:
            message_text += f'• "{query[:30]}...": {count} раз\n'

    await message.answer(message_text, parse_mode="HTML")


async def get_enhanced_statistics(message: Message):
    user_id = str(message.from_user.id)

    async with AsyncSessionLocal() as session:
        # Get user
        user_stmt = select(User).where(User.telegram_id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            return None

        # Get all user requests with responses count
        requests_stmt = (
            select(Request, func.count(Response.id).label("responses_count"))
            .outerjoin(Response, Request.id == Response.request_id)
            .where(Request.user_id == user.id)
            .group_by(Request.id)
        )

        requests_result = await session.execute(requests_stmt)
        requests_data = requests_result.all()

        # Calculate various statistics
        total_requests = len(requests_data)
        total_responses = sum(r.responses_count for r in requests_data)

        # Get time-based statistics
        if requests_data:
            # Requests by hour of day
            hour_stmt = (
                select(
                    func.extract("hour", Request.created_at).label("hour"),
                    func.count(Request.id).label("count"),
                )
                .where(Request.user_id == user.id)
                .group_by("hour")
                .order_by("hour")
            )

            hour_result = await session.execute(hour_stmt)
            peak_hours = hour_result.all()

            # Most active day of week
            weekday_stmt = (
                select(
                    func.extract("dow", Request.created_at).label("weekday"),
                    func.count(Request.id).label("count"),
                )
                .where(Request.user_id == user.id)
                .group_by("weekday")
                .order_by("count")
            )

            weekday_result = await session.execute(weekday_stmt)
            active_days = weekday_result.all()

        # Get most common queries
        query_stmt = (
            select(Request.query, func.count(Request.id).label("count"))
            .where(Request.user_id == user.id)
            .group_by(Request.query)
            .order_by(func.count(Request.id).desc())
            .limit(10)
        )

        query_result = await session.execute(query_stmt)
        popular_queries = query_result.all()

        # Prepare comprehensive statistics
        stats = {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "peak_hours": peak_hours if "peak_hours" in locals() else [],
            "popular_queries": popular_queries,
            "active_days": active_days if "active_days" in locals() else [],
            "response_rate": total_responses / total_requests
            if total_requests > 0
            else 0,
        }

        return stats

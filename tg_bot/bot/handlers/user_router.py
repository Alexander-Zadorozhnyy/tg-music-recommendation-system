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
            # Handle short queries
            display_query = query[:30] + "..." if len(query) > 30 else query
            message_text += f'• "{display_query}": {count} раз\n'
        message_text += "\n"

    if stats["active_days"]:
        message_text += "🗓️ <b>Активность по дням недели:</b>\n"
        days_map = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье",
        }

        # Sort by count (most active days first)
        sorted_days = sorted(stats["active_days"], key=lambda x: x[1], reverse=True)

        for day_num, count in sorted_days[:3]:  # Show top 3 days
            day_name = days_map.get(int(day_num), f"День {day_num}")
            message_text += f"• {day_name}: {count} запросов\n"

    if stats["total_active_days"]:
        message_text += f"📅 <b>Дней с активностью: {stats['total_active_days']}</b>\n\n"

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

        # Get most active days of week (0=Monday, 6=Sunday)
        weekday_stmt = (
            select(
                func.extract("dow", Request.created_at).label("weekday"),
                func.count(Request.id).label("count"),
            )
            .where(Request.user_id == user.id)
            .group_by("weekday")
            .order_by(func.count(Request.id).desc())
        )

        weekday_result = await session.execute(weekday_stmt)
        active_days = [
            (int(row.weekday), int(row.count)) for row in weekday_result.all()
        ]

        # Get most active hours of day
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
        peak_hours = [(int(row.hour), int(row.count)) for row in hour_result.all()]

        # Get most common queries
        query_stmt = (
            select(Request.query, func.count(Request.id).label("count"))
            .where(Request.user_id == user.id)
            .group_by(Request.query)
            .order_by(func.count(Request.id).desc())
            .limit(10)
        )

        query_result = await session.execute(query_stmt)
        popular_queries = [(row.query, int(row.count)) for row in query_result.all()]

        # Calculate unique active days count
        unique_days_stmt = select(func.date(Request.created_at).distinct()).where(
            Request.user_id == user.id
        )
        unique_days_result = await session.execute(unique_days_stmt)
        total_active_days = len(unique_days_result.all())

        # Prepare comprehensive statistics
        stats = {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "peak_hours": peak_hours,
            "popular_queries": popular_queries,
            "active_days": active_days,
            "total_active_days": total_active_days,  # New field: count of unique days with activity
            "response_rate": total_responses / total_requests
            if total_requests > 0
            else 0,
        }

        return stats

from db import async_session
from db.models.conversation_message import ConversationMessage
from db.models.user import User
from db.models.question import Question, InputKind
from db.models.run import Run, RunMode, RunStatus
from db.models.solution_step import SolutionStep
from db.models.attachment import Attachment
from sqlalchemy import select, desc


async def get_or_create_user(tg_id: int) -> User:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                user = User(tg_id=tg_id)
                session.add(user)
                await session.flush()
            return user


async def get_user_pk_by_tg(tg_id: int) -> int | None:
    async with async_session() as session:
        return await session.scalar(select(User.id).where(User.tg_id == tg_id))


async def save_question(
    user_pk: int, input_kind: InputKind, type_text: str | None = None
) -> Question:
    async with async_session() as session:
        async with session.begin():
            q = Question(user_id=user_pk, input_kind=input_kind, type_text=type_text)
            session.add(q)
            await session.flush()
            return q


async def save_run(question_id: int, mode: RunMode, ocr_text: str | None = None) -> Run:
    async with async_session() as session:
        async with session.begin():
            r = Run(
                question_id=question_id,
                mode=mode,
                ocr_text=ocr_text,
                status=RunStatus.PENDING,
            )
            session.add(r)
            await session.flush()
            return r


async def finish_run_ok(run_id: int, final_answer: str, steps_count: int = 0):
    async with async_session() as session:
        async with session.begin():
            run = await session.get(Run, run_id)
            if run:
                run.final_answer = final_answer
                run.steps_count = steps_count
                run.status = RunStatus.OK


async def add_solution_step(run_id: int, step_no: int, text_step: str):
    async with async_session() as session:
        async with session.begin():
            step = SolutionStep(run_id=run_id, step_no=step_no, text_step=text_step)
            session.add(step)


async def add_attachment(
    question_id: int | None,
    run_id: int | None,
    file: str,
    mime: str | None = None,
    size_bytes: int | None = None,
):
    async with async_session() as session:
        async with session.begin():
            att = Attachment(
                question_id=question_id,
                run_id=run_id,
                file=file,
                mime=mime,
                size_bytes=size_bytes,
            )
            session.add(att)


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


# Save a new message for a user
async def save_message(tg_id: int, text: str) -> None:
    async with async_session() as session:
        # Ensure user exists
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()  # commit to generate id for FK

        # Add new message
        msg = ConversationMessage(user_id=user.tg_id, message=text)
        session.add(msg)
        await session.commit()


# Get the last message for a user
async def get_last_message(tg_id: int) -> str | None:
    async with async_session() as session:
        result = await session.scalar(
            select(ConversationMessage)
            .where(ConversationMessage.user_id == tg_id)
            .order_by(desc(ConversationMessage.created_at))
        )
        if result:
            return result.message
        return None

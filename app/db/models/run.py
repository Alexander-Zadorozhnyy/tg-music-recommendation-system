from datetime import datetime
from sqlalchemy import ForeignKey, Enum, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
import enum


class RunMode(str, enum.Enum):
    INSTANT = "I"
    STEP = "S"


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    ocr_text: Mapped[str] = mapped_column(Text, nullable=True)
    mode: Mapped[RunMode] = mapped_column(Enum(RunMode), nullable=False)
    steps_count: Mapped[int] = mapped_column(Integer, default=0)
    final_answer: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.PENDING)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    question: Mapped["Question"] = relationship(back_populates="runs")

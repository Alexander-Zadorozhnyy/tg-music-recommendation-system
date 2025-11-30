from datetime import datetime
from sqlalchemy import ForeignKey, Enum, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
import enum


class InputKind(str, enum.Enum):
    TEXT = "T"
    IMAGE = "I"
    AUDIO = "A"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    input_kind: Mapped[InputKind] = mapped_column(Enum(InputKind), nullable=False)
    type_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    runs: Mapped[list["Run"]] = relationship(back_populates="question")

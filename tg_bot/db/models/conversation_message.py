from sqlalchemy import BigInteger, ForeignKey, Column, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Optional: relationship to user
    user: Mapped["User"] = relationship("User", back_populates="messages")

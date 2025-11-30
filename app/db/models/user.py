from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True, nullable=False)

    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="user", cascade="all, delete-orphan"
    )

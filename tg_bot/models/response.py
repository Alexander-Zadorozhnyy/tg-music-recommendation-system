from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from datetime import datetime
from .user import User
from .request import Request


class Response(SQLModel, table=True):
    __tablename__ = "responses"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    request_id: int = Field(foreign_key="requests.id")
    response_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="responses")
    request: Request = Relationship(back_populates="responses")

from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime
from .user import User
from .response import Response


class Request(SQLModel, table=True):
    __tablename__ = "requests"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    song_credits: str = Field(default="", max_length=1000)
    query: str = Field(max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="requests")
    responses: List[Response] = Relationship(back_populates="request")

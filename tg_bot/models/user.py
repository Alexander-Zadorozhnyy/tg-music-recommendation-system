from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .request import Request
from .response import Response


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    telegram_id: str = Field(unique=True, index=True)
    username: Optional[str] = Field(default=None, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)

    requests: List[Request] = Relationship(back_populates="user")
    responses: List[Response] = Relationship(back_populates="user")

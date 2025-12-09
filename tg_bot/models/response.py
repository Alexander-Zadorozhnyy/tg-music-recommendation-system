from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime


class Response(SQLModel, table=True):
    __tablename__ = "responses"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    request_id: int = Field(foreign_key="requests.id")
    response_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

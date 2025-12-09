from sqlmodel import SQLModel, Field, Column, Text
from datetime import datetime


class Result(SQLModel, table=True):
    __tablename__ = "result"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    song_text: str = Field(sa_column=Column(Text))
    query: str = Field(max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

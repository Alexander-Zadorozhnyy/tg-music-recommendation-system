from typing import Optional
from sqlmodel import SQLModel, Field


class History(SQLModel, table=True):
    __tablename__ = "history"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.telegram_id", index=True)
    query: str = Field(max_length=1000)
    is_relevant: bool
    response: Optional[str] = Field(default=None, sa_column_kwargs={"nullable": True})

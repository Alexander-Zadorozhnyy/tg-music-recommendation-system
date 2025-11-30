from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class SolutionStep(Base):
    __tablename__ = "solution_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    step_no: Mapped[int] = mapped_column(Integer)
    text_step: Mapped[str] = mapped_column(Text, nullable=False)

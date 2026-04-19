from datetime import date
from typing import Optional

from api.model.base_model import Base
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.habit import Habit


class Log(Base):
    __tablename__ = "logs"

    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), index=True)
    completed_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    habit: Mapped["Habit"] = relationship(back_populates="logs")

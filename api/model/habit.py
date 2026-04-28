from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base_model import Base

if TYPE_CHECKING:
    from model.log import Log
    from model.user import User


class Habit(Base):
    __tablename__ = "habits"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    frequency: Mapped[str] = mapped_column(String(50))  # e.g., 'daily', 'weekly'

    user: Mapped["User"] = relationship(back_populates="habits")
    logs: Mapped[List["Log"]] = relationship(back_populates="habit", cascade="all, delete-orphan")

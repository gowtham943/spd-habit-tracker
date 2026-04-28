from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base_model import Base

if TYPE_CHECKING:
    from model.user import User


class Task(Base):
    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[date] = mapped_column(Date)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Link to the user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="tasks")

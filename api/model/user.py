from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base_model import Base

if TYPE_CHECKING:
    from model.habit import Habit
    from model.task import Task


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=False, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    # Relationship to habits
    habits: Mapped[List["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")

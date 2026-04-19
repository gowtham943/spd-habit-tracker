from typing import List

from api.model.base_model import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.habit import Habit


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Relationship to habits
    habits: Mapped[List["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")

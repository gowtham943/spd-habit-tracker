from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict
from schema.habit_schema import HabitResponse


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass  # Just requires the name from UserBase


class UserResponse(UserBase):
    id: int
    created_at: datetime
    # Optionally include all habits (and their logs) when returning a user
    habits: List[HabitResponse] = []

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from model.schema.habit_schema import HabitResponse


class UserBase(BaseModel):
    user_name: str
    display_name: str
    password: str


class UserCreate(UserBase):
    pass  # Just requires the name from UserBase


class UserResponse(UserBase):
    id: int
    created_at: datetime
    # Optionally include all habits (and their logs) when returning a user
    habits: List[HabitResponse] = []

    model_config = ConfigDict(from_attributes=True)

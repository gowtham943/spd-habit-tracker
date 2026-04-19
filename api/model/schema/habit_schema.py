from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict
from schema.log_schema import LogResponse


class HabitBase(BaseModel):
    name: str
    frequency: str


class HabitCreate(HabitBase):
    user_id: int


class HabitResponse(HabitBase):
    id: int
    user_id: int
    created_at: datetime
    # Optionally include all logs for this habit when returning a habit
    logs: List[LogResponse] = []

    model_config = ConfigDict(from_attributes=True)

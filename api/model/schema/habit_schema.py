from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from model.schema.log_schema import LogResponse


class HabitBase(BaseModel):
    name: str
    frequency: str


class HabitCreate(HabitBase):
    pass


class HabitResponse(HabitBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitWithLogsResponse(HabitResponse):
    logs: List[LogResponse] = []

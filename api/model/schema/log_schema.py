from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    completed_date: date
    status: str = "completed"
    notes: Optional[str] = None


class LogCreate(LogBase):
    habit_id: int


class LogResponse(LogBase):
    id: int
    habit_id: int

    model_config = ConfigDict(from_attributes=True)

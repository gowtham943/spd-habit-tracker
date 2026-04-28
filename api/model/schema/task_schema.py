from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: date


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    user_id: int
    is_completed: bool

    model_config = ConfigDict(from_attributes=True)

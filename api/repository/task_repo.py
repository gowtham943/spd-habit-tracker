from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_tasks_by_user(self, user_id: int) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id).order_by(Task.due_date.asc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def mark_completed(self, task: Task) -> Task:
        task.is_completed = True
        updated_task = await self.session.merge(task)
        await self.session.commit()
        return updated_task

    async def delete_task(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()

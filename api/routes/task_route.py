from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth import User  # Adjust based on your auth file

from config.database_config import db
from dependency.auth import get_current_user
from model.schema.task_schema import TaskCreate, TaskResponse
from model.task import Task
from repository.task_repo import TaskRepository

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_repo(session: AsyncSession = Depends(db.get_session)) -> TaskRepository:
    return TaskRepository(session)


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task(
    task_in: TaskCreate, current_user: User = Depends(get_current_user), repo: TaskRepository = Depends(get_task_repo)
):
    new_task = Task(**task_in.model_dump(), user_id=current_user.id)
    return await repo.create_task(new_task)


@task_router.get("/", response_model=List[TaskResponse])
async def read_tasks(current_user: User = Depends(get_current_user), repo: TaskRepository = Depends(get_task_repo)):
    return await repo.get_tasks_by_user(current_user.id)


@task_router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int, current_user: User = Depends(get_current_user), repo: TaskRepository = Depends(get_task_repo)
):
    task = await repo.get_task_by_id(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return await repo.mark_completed(task)

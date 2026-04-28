from fastapi import APIRouter, Depends, HTTPException, status
from realtime import List
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth import User

from config.database_config import db
from dependency.auth import get_current_user
from model.log import Log
from model.schema.log_schema import LogCreate, LogResponse
from repository.habit_repo import HabitRepository
from repository.log_repo import LogRepository
from routes.habit_route import get_habit_repo


def get_log_repo(session: AsyncSession = Depends(db.get_session)) -> LogRepository:
    return LogRepository(session)


log_router = APIRouter(prefix="/logs", tags=["logs"])


@log_router.post("/habits/{habit_id}", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def add_log(
    habit_id: int,
    log_in: LogCreate,
    current_user: User = Depends(get_current_user),
    habit_repo: HabitRepository = Depends(get_habit_repo),
    log_repo: LogRepository = Depends(get_log_repo),
):
    """Logs an entry for a specific habit."""
    # 1. Verify the habit exists and belongs to the user
    habit = await habit_repo.get_habit_by_id(habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found or access denied")

    # 2. Check for duplicate daily logs
    existing_log = await log_repo.get_log_by_habit_and_date(habit_id, log_in.completed_date)
    if existing_log:
        raise HTTPException(status_code=400, detail="Habit already logged for this date")

    # 3. Create the log
    new_log = Log(habit_id=habit_id, completed_date=log_in.completed_date, status=log_in.status, notes=log_in.notes)
    return await log_repo.create_log(new_log)


@log_router.get("/habits/{habit_id}", response_model=List[LogResponse])
async def read_logs(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    habit_repo: HabitRepository = Depends(get_habit_repo),
    log_repo: LogRepository = Depends(get_log_repo),
):
    """Fetches all history logs for a specific habit."""
    habit = await habit_repo.get_habit_by_id(habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")

    return await log_repo.get_logs_by_habit(habit_id)


@log_router.get("/{log_id}", response_model=List[LogResponse])
async def read_log(log_id: int, log_repo: LogRepository = Depends(get_log_repo)):
    return await log_repo.get_log_by_id(log_id)


@log_router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    log_repo: LogRepository = Depends(get_log_repo),
    habit_repo: HabitRepository = Depends(get_habit_repo),
):
    """Deletes a specific log entry."""
    log = await log_repo.get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # Security check: Ensure the habit attached to this log belongs to the user
    habit = await habit_repo.get_habit_by_id(log.habit_id)
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await log_repo.delete_log(log)

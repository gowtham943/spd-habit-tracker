from fastapi import APIRouter, Depends, HTTPException, status
from realtime import List
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth import User

from config.database_config import db
from dependency.auth import get_current_user
from model.habit import Habit
from model.schema.habit_schema import HabitCreate, HabitResponse
from repository.habit_repo import HabitRepository


def get_habit_repo(session: AsyncSession = Depends(db.get_session)) -> HabitRepository:
    return HabitRepository(session)


habit_router = APIRouter(prefix="/habits", tags=["habits"])


@habit_router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def add_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),  # The Bouncer
    repo: HabitRepository = Depends(get_habit_repo),
):
    """Creates a new habit linked to the logged-in user."""
    new_habit = Habit(
        name=habit_in.name,
        frequency=habit_in.frequency,
        user_id=current_user.id,  # Automatically link to the token holder!
    )
    return await repo.create_habit(new_habit)


@habit_router.get("/", response_model=List[HabitResponse])
async def read_habits(current_user: User = Depends(get_current_user), repo: HabitRepository = Depends(get_habit_repo)):
    """Fetches all habits belonging to the logged-in user."""
    return await repo.get_habits_by_user(current_user.id)


# read habits by id
@habit_router.get("/{habit_id}", response_model=HabitResponse)
async def read_habit(habit_id: int, repo: HabitRepository = Depends(get_habit_repo)):
    return await repo.get_habit_by_id(habit_id)


@habit_router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int, current_user: User = Depends(get_current_user), repo: HabitRepository = Depends(get_habit_repo)
):
    """Deletes a specific habit (must belong to user)."""
    habit = await repo.get_habit_by_id(habit_id)

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this habit")

    await repo.delete_habit(habit)

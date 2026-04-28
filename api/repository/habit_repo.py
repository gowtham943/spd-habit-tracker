from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from model.habit import Habit


class HabitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_habit(self, habit: Habit) -> Habit:
        self.session.add(habit)
        await self.session.commit()
        await self.session.refresh(habit)
        return habit

    async def get_habit_by_id(self, habit_id: int) -> Optional[Habit]:
        statement = select(Habit).where(Habit.id == habit_id).options(selectinload(Habit.logs))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_habits_by_user(self, user_id: int) -> list[Habit]:
        """Fetches all habits for a specific user ID."""
        statement = (
            select(Habit)
            .where(Habit.user_id == user_id)  # Filter by user_id!
            .options(selectinload(Habit.logs))
            .order_by(Habit.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_habit(self, habit: Habit) -> Habit:
        updated_habit = await self.session.merge(habit)
        await self.session.commit()
        return updated_habit

    async def delete_habit(self, habit: Habit) -> None:
        await self.session.delete(habit)
        await self.session.commit()

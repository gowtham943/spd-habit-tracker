from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.log import Log


class LogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_log(self, log: Log) -> Log:
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def get_log_by_id(self, log_id: int) -> Optional[Log]:
        statement = select(Log).where(Log.id == log_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_log_by_habit_and_date(self, habit_id: int, target_date: date) -> Optional[Log]:
        """
        Fetches a log for a specific habit on a specific date.
        Crucial for checking if a user already completed a habit today!
        """
        statement = select(Log).where(Log.habit_id == habit_id, Log.completed_date == target_date)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_logs_by_habit(self, habit_id: int) -> Sequence[Log]:
        """
        Fetches ALL logs for a specific habit.
        Used for building streaks, calendars, and charts.
        """
        statement = select(Log).where(Log.habit_id == habit_id).order_by(Log.completed_date.desc())
        result = await self.session.execute(statement)

        # scalars().all() extracts the list of Log objects from the SQLAlchemy result rows
        return result.scalars().all()

    async def update_log(self, log: Log) -> Log:
        updated_log = await self.session.merge(log)
        await self.session.commit()
        return updated_log

    async def delete_log(self, log: Log) -> None:
        await self.session.delete(log)
        await self.session.commit()

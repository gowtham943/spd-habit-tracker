from sqlalchemy import select

from model.user import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_user(self, user) -> User:
        updated_user = await self.session.merge(user)
        await self.session.commit()
        return updated_user

    async def delete_user(self, user) -> None:
        await self.session.delete(user)
        await self.session.commit()

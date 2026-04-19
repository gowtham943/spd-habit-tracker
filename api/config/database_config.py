from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.config_setting import settings


class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"statement_cache_size": 0},
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Creates a new database session for a request and safely closes it afterward.
        """
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                # The async with block automatically handles closing,
                await session.close()

    async def close_database(self):
        """Disposes of the connection pool gracefully on shutdown."""
        await self.engine.dispose()
        print("Database connection pool closed.")


db = Database(settings.DATABASE_URL)

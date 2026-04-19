from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.config_setting import settings
from config.database_config import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down API...")
    await db.close_database()


app = FastAPI(title="SPD Habit Tracker API", version="0.1.0")

print(settings.DATABASE_URL)


@app.get("/db-health")
async def check_db_health(session: AsyncSession = Depends(db.get_session)):
    result = await session.execute(text("SELECT 1"))
    return {"status": "Database is connected and healthy!", "result": result.scalar()}


@app.get("/health")
def read_health():
    return {"status": "healthy"}

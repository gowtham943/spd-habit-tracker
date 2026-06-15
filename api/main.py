from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.database_config import db
from routes.auth_route import auth_router
from routes.chat_route import chat_router
from routes.habit_route import habit_router
from routes.log_route import log_router
from routes.mcp_route import mcp_asgi_subapp
from routes.task_route import task_router
from routes.user_route import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down API...")
    await db.close_database()


app = FastAPI(title="SPD Habit Tracker API", version="0.1.0")
app.include_router(auth_router)
app.include_router(habit_router)
app.include_router(log_router)
app.include_router(user_router)
app.include_router(task_router)
app.mount("/mcp", mcp_asgi_subapp)
app.include_router(chat_router)

from datetime import date

from fastmcp import FastMCP

from config.database_config import db
from model.habit import Habit
from model.log import Log
from model.task import Task
from repository.habit_repo import HabitRepository
from repository.log_repo import LogRepository
from repository.task_repo import TaskRepository
from service.rag_service import sync_log_to_vector_store

# 1. Initialize the FastMCP Server instance
mcp_app = FastMCP("HabitAgent-Core")


# ---------------------------------------------------------
# MCP TOOL: Map directly to your TaskRepository
# ---------------------------------------------------------
@mcp_app.tool()
async def create_user_task(title: str, description: str, user_id: str) -> str:
    """
    Creates and schedules a new task/todo item for a specific user.
    Use this tool whenever the user explicitly asks to add, schedule, or create a task,
    reminder, or todo item.

    Parameters:
    - title: The name or title of the task.
    - description: Additional details or context about the task.
    - user_id: The unique database string ID of the current logged-in user.
    """

    # Create a wrapper function to safely execute and clean up the session generator
    async def execute_in_session():
        async for session in db.get_session():
            repo = TaskRepository(session)
            # Construct your existing SQLAlchemy Model exactly like your router does
            new_task = Task(title=title, description=description, user_id=user_id)

            # Execute through your existing repository layer
            created_task = await repo.create_task(new_task)

            # Return the success string
            return f"Success: Task '{created_task.title}' has been created with ID {created_task.id}."

    try:
        result = await execute_in_session()
        if result:
            return result
        return "Error: Database session ended without creating a task."
    except Exception as e:
        return f"Error executing task creation via database: {str(e)}"


# (Keep your existing FastMCP initialization and create_user_task tool here)


# ---------------------------------------------------------
# MCP TOOL: Map directly to your Habit & Log Repositories
# ---------------------------------------------------------
@mcp_app.tool()
async def log_habit_completion(habit_id: int, status: str, user_id: str, notes: str = None) -> str:
    """
    Logs an activity entry, check-in, or tracking update for a specific habit for today.
    Use this tool whenever the user indicates they have completed, missed, or partially done a habit.

    Parameters:
    - habit_id: The unique integer database ID of the habit being tracked.
    - status: The progress state of the habit. Must be exactly 'completed', 'missed', or 'partial'.
    - user_id: The unique database string ID of the current authenticated user.
    - notes: Optional commentary, context, or thoughts from the user regarding today's habit execution.
    """
    # Establish a clean async session from your SQLAlchemy engine pool
    async for session in db.get_session():
        habit_repo = HabitRepository(session)
        log_repo = LogRepository(session)

        try:
            numeric_user_id = int(user_id)
            # 1. Map to your exact business logic: Verify ownership
            habit = await habit_repo.get_habit_by_id(habit_id)
            if not habit or habit.user_id != numeric_user_id:
                return "Error: Habit not found or access denied for your current user configuration."

            # 2. Map to your exact business logic: Check for duplicate daily logs
            today = date.today()
            existing_log = await log_repo.get_log_by_habit_and_date(habit_id, today)
            if existing_log:
                return f"Info: This habit was already logged for today ({today}). No changes were made."

            # 3. Create the log using your existing Model layer
            new_log = Log(
                habit_id=habit_id, completed_date=today, status=status, notes=notes or "Logged via AI Sidebar Assistant"
            )
            await log_repo.create_log(new_log)

            # 4. Sync the log to your local RAG vector store for semantic search
            # If the user added free-form text notes, automatically embed them into our vector brain!
            if notes:
                await sync_log_to_vector_store(
                    text_content=f"Habit: {habit.name} marked as {status}. Notes: {notes}",
                    user_id=user_id,
                    habit_id=habit_id,
                )
            return f"Success: Logged daily entry for habit '{habit.name}' as '{status}'."

        except Exception as e:
            return f"Error logging habit execution via database: {str(e)}"


# (Keep your existing FastMCP initialization, task, and log tools here)


# ---------------------------------------------------------
# MCP READ TOOL: Fetch Active Trackable Habits
# ---------------------------------------------------------
@mcp_app.tool()
async def get_user_habits(user_id: str) -> str:
    """
    Retrieves a complete list of all active habits currently tracked by the user.
    Always call this tool first if the user asks you to log an entry but does not
    provide the explicit numerical habit_id, or if they ask what habits they are tracking.

    Parameters:
    - user_id: The unique database string ID of the current authenticated user.
    """
    async for session in db.get_session():
        repo = HabitRepository(session)
        try:
            numeric_user_id = int(user_id)
            # Leverage your existing repository get method
            habits = await repo.get_habits_by_user(numeric_user_id)

            if not habits:
                return "User is not tracking any habits yet. Tell them to create one!"

            # Format a clear text list for the LLM to easily parse names and IDs
            habit_list = ["Here are the user's current trackable habits:"]
            for h in habits:
                habit_list.append(f"- ID: {h.id} | Name: {h.name} | Frequency: {h.frequency}")

            return "\n".join(habit_list)

        except Exception as e:
            return f"Error retrieving tracking configurations: {str(e)}"


@mcp_app.tool()
async def create_new_user_habit(name: str, frequency: str, user_id: str) -> str:
    """
    Creates and initializes a brand new trackable habit in the database for the user.
    Use this tool whenever the user explicitly asks to add, track, or create a new habit
    (e.g., 'track a new habit called drinking coffee daily').

    Parameters:
    - name: The name or title of the habit (e.g., 'drinking coffee').
    - frequency: How often they want to do it (e.g., 'daily', 'weekly'). Default to 'daily' if not specified.
    - user_id: The unique database string ID of the current logged-in user.
    """
    async for session in db.get_session():
        repo = HabitRepository(session)
        try:
            numeric_user_id = int(user_id)
            # Construct the exact SQLAlchemy object your database structure expects
            new_habit = Habit(name=name, frequency=frequency, user_id=numeric_user_id)
            created_habit = await repo.create_habit(new_habit)

            # If the user added free-form text notes, automatically embed them into our vector brain!
            if created_habit:
                await sync_log_to_vector_store(
                    text_content=f"Habit: {created_habit.name} has been created",
                    user_id=user_id,
                    habit_id=str(created_habit.id),
                )

            return f"Success: Habit '{created_habit.name}' has been created with ID {created_habit.id}."
        except Exception as e:
            return f"Error executing habit creation via database: {str(e)}"


mcp_asgi_subapp = mcp_app.http_app(transport="sse")

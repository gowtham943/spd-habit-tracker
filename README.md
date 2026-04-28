# spd-habit-tracker

## Overview
**Habit Tracker** is a gamified, full-stack productivity dashboard designed to help users track daily habits, manage one-off tasks (Side Quests), and visualize their progress over time. 


**Tech Stack:**
* **Frontend:** Streamlit, Pandas, Plotly (for gamified data visualization), Streamlit-Cookies-Controller (for persistent sessions).
* **Backend:** FastAPI, SQLAlchemy 2.0 (Async), asyncpg, Alembic, JWT Authentication.
* **Database:** PostgreSQL.
* **Infrastructure:** Docker, Docker Compose, `uv` (Astral's fast Python package manager).

---

## Structure
The project is split into two isolated microservices (Backend API and Frontend UI) orchestrated by Docker Compose.

```text
habit-tracker/
│
├── api/                     # FastAPI Backend Microservice
│   ├── config/              # Database and App settings
│   ├── dependency/          # JWT Auth and Session dependencies
│   ├── model/               # SQLAlchemy Models & Pydantic Schemas
│   ├── repository/          # Database queries (Habits, Tasks, Logs, Users)
│   ├── routes/              # FastAPI endpoint routers
│   ├── main.py              # FastAPI Application Entrypoint
│   ├── pyproject.toml       # Backend dependencies (managed by uv)
│   └── Dockerfile           # Backend container instructions
│
├── ui/                      # Streamlit Frontend Microservice
│   ├── client/              # API HTTP Client wrappers (httpx)
│   ├── views/               # UI Pages (Home, Dashboard, Habits, Tracker, Tasks)
│   ├── main.py              # Streamlit Router & Auth wrapper
│   ├── pyproject.toml       # Frontend dependencies (managed by uv)
│   └── Dockerfile           # Frontend container instructions
│
├── .env                     # Global Environment variables
└── docker-compose.yml       # Master container orchestrator
```

## Local Setup
If you prefer to run the application natively on your machine without Docker, follow these steps.

1. Prerequisites
Python 3.11+

PostgreSQL running locally on port 5432.

uv package manager installed (curl -LsSf https://astral.sh/uv/install.sh | sh).

2. Configure Environment Variables
Create a .env file in the root directory. Note: When running locally, ensure the hosts are set to localhost or 127.0.0.1.


# Database (Localhost)
DATABASE_URL="postgresql+asyncpg://postgres:g9439@localhost:5432/habit_tracker_db"
DIRECT_URL="postgresql://postgres:g9439@localhost:5432/habit_tracker_db"

# API & Security
API_BASE_URL="[http://127.0.0.1:8000](http://127.0.0.1:8000)"
JWT_SECRET_KEY="super_secret_key_change_me_in_production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
3. Run the Backend (API)
Open a terminal, navigate to the api folder, and run:

```text
cd api
uv pip install -r pyproject.toml
uv run alembic upgrade head          # Creates the database tables
uv run uvicorn main:app --reload     # Starts the API on port 8000
API Docs available at: http://127.0.0.1:8000/docs
```

4. Run the Frontend (UI)
Open a second terminal, navigate to the ui folder, and run:

```text
cd ui
uv pip install -r pyproject.toml
uv run streamlit run main.py         # Starts the UI on port 8501
App available at: http://localhost:8501
```

Docker Setup
The easiest and most robust way to run Habit Hero is using Docker Compose. This handles the PostgreSQL database, networking, and microservices automatically.

1. Prerequisites
Docker Desktop installed and running.

2. Configure Environment Variables
Create a .env file in the root directory. Note: When running in Docker, the services communicate using their container names (db and api).

```text
# Database (Docker Network)
DATABASE_URL="postgresql+asyncpg://postgres:g9439@db:5432/habit_tracker_db"
DIRECT_URL="postgresql://postgres:g9439@db:5432/habit_tracker_db"

# API & Security
API_BASE_URL="http://api:8000"
JWT_SECRET_KEY="super_secret_key_change_me_in_production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

3. Launch the Fleet
Open your terminal in the root folder (where docker-compose.yml is located) and run:

```text
docker compose up --build
(Tip: Add -d at the end to run it in detached/background mode).
```

4. Access the Application
Web Dashboard (UI): http://localhost:8501

Backend Swagger Docs (API): http://localhost:8000/docs

To stop and tear down the containers:

```text
docker compose down
```
FROM python:3.11-slim

# Install uv directly from Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml .
# If you have a uv.lock file, uncomment the line below:
# COPY uv.lock .

# Install dependencies into the system environment
RUN uv pip install --system -r pyproject.toml

# Copy the rest of your application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run migrations and then start the server
# Using sh -c allows us to chain the commands safely
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
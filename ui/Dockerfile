FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
# COPY uv.lock .

RUN uv pip install --system -r pyproject.toml

COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Start Streamlit in headless mode
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
import httpx
import logging
from config.app_config import settings
# Point this to your local FastAPI server


def login(username, password):
    """Hits the OAuth2 login endpoint and returns the JWT."""
    # OAuth2 in FastAPI requires standard form data, NOT json!
    data = {"username": username, "password": password}
    try:
        response = httpx.post(f"{settings.API_BASE_URL}/auth/login", data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        logging.error(f"Connection error: {e}")
    return None


def fetch_habits(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{settings.API_BASE_URL}/habits/", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []


def add_habit(token, name, frequency):
    """Updated to use name and frequency"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": name, "frequency": frequency}
    response = httpx.post(
        f"{settings.API_BASE_URL}/habits/", json=payload, headers=headers
    )
    return response.status_code == 201


def log_habit(token, habit_id, selected_date):
    """Logs a habit for ANY selected date."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        # Convert the Streamlit date object into a string for FastAPI
        "completed_date": selected_date.isoformat(),
        "status": "completed",
        "notes": "Did it!",
    }

    response = httpx.post(
        f"{settings.API_BASE_URL}/logs/habits/{habit_id}", json=payload, headers=headers
    )

    if response.status_code == 201:
        return True, "Level Up!"
    elif response.status_code == 400:
        return False, "Quest already completed on this day!"
    elif response.status_code == 422:
        print(f"FASTAPI 422 ERROR: {response.json()}")
        return False, "Data validation failed."

    return False, f"Failed to log. Status: {response.status_code}"


def get_current_user(token):
    """Fetches the full user profile using the JWT token."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.get(f"{settings.API_BASE_URL}/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch user: {e}")
    return None


def register_user(username, display_name, password):
    """Hits the /users/enroll endpoint to create a new user."""
    payload = {"username": username, "display_name": display_name, "password": password}
    try:
        response = httpx.post(f"{settings.API_BASE_URL}/users/enroll", json=payload)
        return response.status_code == 201
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return False


def fetch_logs(token, habit_id):
    """Fetches all historical logs for a specific habit."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(
        f"{settings.API_BASE_URL}/logs/habits/{habit_id}", headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return []


def fetch_tasks(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{settings.API_BASE_URL}/tasks/", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []


def add_task(token, name, description, due_date):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": name,
        "description": description,
        "due_date": due_date.isoformat(),
    }
    response = httpx.post(
        f"{settings.API_BASE_URL}/tasks/", json=payload, headers=headers
    )
    return response.status_code == 201


def complete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.patch(
        f"{settings.API_BASE_URL}/tasks/{task_id}/complete", headers=headers
    )
    return response.status_code == 200

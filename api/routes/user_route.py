from fastapi import APIRouter, Depends, HTTPException, status

from dependency.auth import get_current_user, get_user_repo
from enums.users_opt import UserOps
from model.schema.user_schema import UserCreate
from model.user import User
from repository.user_repo import UserRepository
from utils.security import get_password_hash

user_router = APIRouter(prefix="/user", tags=["users"])


@user_router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_user(user_in: UserCreate, repo: UserRepository = Depends(get_user_repo)):
    """Registers a new user into the system."""
    print(f"Attempting to enroll user: {user_in.username}")
    print(UserOps.GOWTHAM, UserOps.PRIYA, UserOps.SANMITHA)
    # Check if username already exists
    if (
        UserOps.GOWTHAM.value not in str(user_in.username).lower()
        and UserOps.PRIYA.value not in str(user_in.username).lower()
        and UserOps.SANMITHA.value not in str(user_in.username).lower()
    ):
        raise HTTPException(status_code=400, detail="Username is not acceptable")
    existing_user = await repo.get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash password and save
    hashed_pw = get_password_hash(user_in.password)

    # Create the SQLAlchemy object and save it
    new_user = User(username=user_in.username, display_name=user_in.display_name, password=hashed_pw)
    saved_user = await repo.create_user(new_user)

    return {"message": "User enrolled successfully", "user_id": saved_user.id}


@user_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Takes a token and returns the full profile of the logged-in user."""
    # current_user is already securely fetched from the database by the Bouncer!
    return {"id": current_user.id, "username": current_user.username, "display_name": current_user.display_name}

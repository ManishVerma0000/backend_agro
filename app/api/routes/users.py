from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from app.api.deps import get_current_user, get_current_active_user
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retrieve users. Only active users have access.
    Note: Full implementation requires fetching all users from DB. For now, returning the current user as an example.
    """
    return [current_user]

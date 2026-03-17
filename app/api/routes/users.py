from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from app.api.deps import get_current_user, get_current_active_user
from app.schemas.user import UserResponse,RegisterUser,LoginUser,LoginWarehouseUser
from app.services.user_service import register_user_to_db,login_warehouse_user;

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



@router.post('/register')
async def register_user(request_body:RegisterUser):
    try:
        result=await register_user_to_db(request_body)
        return  result
    except Exception as e :
        raise HTTPException(status_code=500, detail={
            "message":"internal server error"
        })


@router.post('/login-warehouse-user')
async def login_user(request_body:LoginWarehouseUser):
    try:
        result=await login_warehouse_user(request_body)
        return  {
            "message":"user is logged in successfully",
            "userdetails":result
        }
    except Exception as e :
            raise HTTPException(status_code=500, detail={
                 "message":"internal server error"
            })





# @router.post('/')

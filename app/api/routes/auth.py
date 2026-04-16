from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.schemas.user import Token, UserCreate, UserResponse,LoginUser

router = APIRouter()


@router.post("/register", response_model=Any)
async def register_user(user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    user_by_email = await get_user_by_email(user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
        
    user = await create_user(user_in)
    return user


@router.post('/login',response_model=Any)
async def login_user(request_body:LoginUser):
    if  not request_body.username:
        return {
            "message":"please enter the username"
        }
        
    # Hardcoded admin credentials for the time being
    if request_body.username == "admin" and request_body.password == "admin":
        token = create_access_token("admin_hardcoded_id_123")
        return {
            "message": "User is logged in successfully",
            "token": token
        }

    user = await get_user_by_username(request_body.username)
    if not user:
        return {
            "message":"invalid username"
        }
    
    if not verify_password(request_body.password,user['hashed_password']):
        return {
            "message":"invalid password"
        }
    
    token=create_access_token(str(user["_id"]))
    return{
        "message":"User is logged in successfully",
        "token":token
    }


# @router.post("/login", response_model=Token)
# async def login_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends()
# ) -> Any:
#     """
#     OAuth2 compatible token login, get an access token for future requests.
#     """
#     # The OAuth2 standard uses "username", but we can permit email or username interchangeably
#     # For this example, let's treat the incoming string as a username
#     user = await get_user_by_username(form_data.username)
    
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect email or password")
        
#     if not verify_password(form_data.password, user["hashed_password"]):
#         raise HTTPException(status_code=400, detail="Incorrect email or password")
        
#     if not user["is_active"]:
#         raise HTTPException(status_code=400, detail="Inactive user")

#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     return {
#         "access_token": create_access_token(
#             str(user["_id"]), expires_delta=access_token_expires
#         ),
#         "token_type": "bearer",
#     }

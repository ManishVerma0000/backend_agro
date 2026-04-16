from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from app.api.deps import get_current_user, get_current_active_user
from app.schemas.user import UserResponse, RegisterUser, LoginUser, LoginWarehouseUser
from app.services.user_service import register_user_to_db, login_warehouse_user, send_warehouse_otp
from app.db.session import get_db
from app.core.config import settings
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class OTPRequest(BaseModel):
    email: str


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: dict = Depends(get_current_active_user)):
    """Get current user."""
    return current_user


@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieve users."""
    return [current_user]


@router.post('/register')
async def register_user(request_body: RegisterUser):
    try:
        result = await register_user_to_db(request_body)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error"})


@router.post('/send-warehouse-otp')
async def request_otp(request_body: OTPRequest):
    try:
        result = await send_warehouse_otp(request_body.email)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post('/login-warehouse-user')
async def login_user(request_body: LoginWarehouseUser):
    try:
        result = await login_warehouse_user(request_body)
        return {
            "message": "user is logged in successfully",
            "userdetails": result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "internal server error"})


@router.get('/warehouse/profile/me')
async def read_current_warehouse(token: str = Depends(reusable_oauth2)):
    """
    Get current warehouse profile based on authentication token.
    Dedicated route separate from /me to avoid path conflicts.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=403, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # Validate it's an ObjectId before querying
    try:
        warehouse_id = ObjectId(sub)
    except Exception:
        raise HTTPException(status_code=400, detail="Token does not contain a valid warehouse ID")

    db = get_db()
    warehouse = await db['warehouses'].find_one({"_id": warehouse_id})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found for this token")

    warehouse["id"] = str(warehouse["_id"])
    warehouse["_id"] = str(warehouse["_id"])
    return warehouse

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import TokenPayload
from app.crud.user import get_user_by_id

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(token: str = Depends(reusable_oauth2)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    user = await get_user_by_id(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["id"] = str(user["_id"])
    return user

async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

from app.db.session import get_db
from bson import ObjectId

async def get_current_warehouse(token: str = Depends(reusable_oauth2)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    db = get_db()
    warehouse = await db['warehouses'].find_one({"_id": ObjectId(token_data.sub)})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    warehouse["id"] = str(warehouse["_id"])
    warehouse["_id"] = str(warehouse["_id"])
    return warehouse

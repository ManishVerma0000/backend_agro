from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import TokenPayload
from app.crud.customer import get_customer

reusable_oauth2_mobile = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/mobile/auth/login"
)

async def get_current_customer(token: str = Depends(reusable_oauth2_mobile)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if not token_data.sub:
            raise ValueError("Token sub missing")
    except (JWTError, ValidationError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    customer = await get_customer(token_data.sub)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

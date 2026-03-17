from pydantic import BaseModel, EmailStr
from typing import Optional

# Base properties shared across schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

# Properties stored in DB (including hash)
class UserInDB(UserBase):
    id: str
    hashed_password: str

# Properties to return to client (excluding hash)
class UserResponse(UserBase):
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None


class LoginUser(BaseModel):
    username:str
    password:str


class RegisterUser(BaseModel):
    phone_number:int
    otp: Optional[int] = None



class LoginWarehouseUser(BaseModel):
    phone_number:int
    otp:int   
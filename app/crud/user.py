from typing import Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

async def get_user_by_email(email: str) -> Optional[dict]:
    db = get_db()
    user = await db["users"].find_one({"email": email})
    return user

async def get_user_by_username(username: str) -> Optional[dict]:
    db = get_db()
    user = await db["users"].find_one({"username": username})
    return user

async def get_user_by_id(user_id: str) -> Optional[dict]:
    db = get_db()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return user

async def create_user(user_in: UserCreate) -> dict:
    db = get_db()
    user_dict = user_in.model_dump(exclude={"password"})

    user_dict["hashed_password"] = get_password_hash(user_in.password)
    result = await db["users"].insert_one(user_dict)
    
    user = await get_user_by_id(str(result.inserted_id))
    if user and "_id" in user:
        user["id"] = str(user.pop("_id"))
    return user

# Complex business logic separated from the endpoint
from app.schemas.user import RegisterUser,LoginWarehouseUser
from app.services.otp_service import send_email_otp
from app.db.session import get_db
from bson import ObjectId
from fastapi import HTTPException
from app.core.security import create_access_token

async def register_user_to_db(request_body:RegisterUser):
    is_user_already_exist=await validate_user_email(request_body)
    if is_user_already_exist:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    otp_no= await send_email_otp(request_body.email)
    user_dict = request_body.model_dump()
    user_dict['otp'] = otp_no
    createUserToDb=await create_user(user_dict)
    return createUserToDb

async def create_user(request_body:RegisterUser)-> dict:
    db=get_db()
    result=await db['user'].insert_one(request_body)
    userdetails=await get_user_details_using_id(str(result.inserted_id))
    return userdetails

async def get_user_details_using_id(user_id:str)-> any:
    db=get_db()
    userdetails=await db['user'].find_one({"_id":ObjectId(user_id)})
    if userdetails :
        userdetails["_id"] = str(userdetails["_id"])
        return userdetails
    return {
        "message":"internal server error"
    }


async def login_warehouse_user(request_body:LoginWarehouseUser):
    userdetails=await validate_warehouse_email(request_body)
    if userdetails:
        token = create_access_token(str(userdetails["_id"]))
        userdetails["token"] = token
        return userdetails
    raise HTTPException(status_code=400, detail="Invalid email or OTP")
async def send_warehouse_otp(email: str):
    db=get_db()
    userdetails=await db['warehouses'].find_one({"email": email})
    if not userdetails:
        raise HTTPException(status_code=404, detail="Warehouse with this email not found")
    otp = await send_email_otp(email)
    await db['warehouses'].update_one({"email": email}, {"$set": {"otp": otp}})
    return {"message": "OTP sent successfully"}
async def validate_user_email(request_body):
    db=get_db()
    userdetails=await db['user'].find_one({"email":request_body.email})
    if (userdetails) and userdetails.get('otp')==request_body.otp:
        userdetails["_id"] = str(userdetails["_id"])
        return userdetails
    return None

async def validate_warehouse_email(request_body:LoginWarehouseUser):
    db=get_db()
    userdetails=await db['warehouses'].find_one({"email":request_body.email})
    if (userdetails) and userdetails.get('otp')==request_body.otp:
        userdetails["_id"] = str(userdetails["_id"])
        return userdetails
    return None

    

    


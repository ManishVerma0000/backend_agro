# Complex business logic separated from the endpoint
from app.schemas.user import RegisterUser,LoginWarehouseUser;
from app.services.otp_service import send_otp
from app.db.session import get_db;
from bson import ObjectId
from fastapi import HTTPException;
async def register_user_to_db(request_body:RegisterUser):
    is_user_already_exist=await validate_user_phone_number(request_body.phone_number)
    if is_user_already_exist:
        raise HTTPException(status_code=400, detail="Phone number is already exist")
    otp_no= await send_otp(request_body.phone_number)
    user_dict = request_body.model_dump()
    user_dict['otp'] = otp_no
    createUserToDb=await create_user(user_dict)
    return  createUserToDb

async def create_user(request_body:RegisterUser)-> dict:
    db=get_db()
    # user_dict=request_body.model_dump()
    result=await db['user'].insert_one(request_body)
    userdetails=await get_user_details_using_id(str(result.inserted_id))
    return (userdetails)

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
    is_phone_matched=await validate_user_phone_number(request_body)
    return is_phone_matched



async def validate_user_phone_number(request_body:LoginWarehouseUser):
    db=get_db()
    userdetails=await db['user'].find_one({"phone_number":request_body.phone_number})
    if(userdetails) and userdetails['otp']==request_body.otp:
        userdetails["_id"] = str(userdetails["_id"])
        return userdetails

    

    


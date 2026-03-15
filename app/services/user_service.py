# Complex business logic separated from the endpoint
from app.schemas.user import RegisterUser;
from app.services.otp_service import send_otp
async def register_user_to_db(request_body:RegisterUser):
    is_otp_send= await send_otp(request_body.phone_number)
    return  is_otp_send
from fastapi import APIRouter, HTTPException, Depends
from typing import Any
from app.schemas.customer import SendOtpRequest, VerifyOtpRequest, RegisterRequest, CustomerResponse, CustomerCreate
from app.crud.customer import create_customer, get_customer_by_mobile
from app.core.security import create_access_token

router = APIRouter()

@router.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    # In a real application, you would integrate with an SMS gateway here (Twilio, AWS SNS, etc).
    # For now, we simulate sending a default OTP "1234"
    print(f"Sending mock OTP 1234 to {request.mobileNumber}")
    return {"message": "OTP sent successfully", "success": True}

@router.post("/register", response_model=Any)
async def register(request: RegisterRequest):
    # 1. Verify OTP
    if request.otp != "1234":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # 2. Check if customer already exists
    existing = await get_customer_by_mobile(request.mobileNumber)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this mobile number already exists")
    
    # 3. Create customer
    customer_in = CustomerCreate(**request.model_dump(exclude={"otp"}))
    customer = await create_customer(customer_in)
    
    # 4. Generate Token
    token = create_access_token(str(customer["id"]))
    
    return {
        "message": "Registration successful",
        "token": token,
        "customer": customer
    }

@router.post("/verify-otp", response_model=Any)
async def verify_otp_login(request: VerifyOtpRequest):
    if request.otp != "1234":
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    customer = await get_customer_by_mobile(request.mobileNumber)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found. Please register.")
        
    token = create_access_token(str(customer["id"]))
    
    return {
        "message": "Login successful",
        "token": token,
        "customer": customer
    }

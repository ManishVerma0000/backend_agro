from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from typing import Any, Optional
from app.schemas.customer import SendOtpRequest, VerifyOtpRequest, CustomerResponse, CustomerCreate, CustomerUpdate
from app.crud.customer import create_customer, get_customer_by_mobile, update_customer, get_customer
from app.core.security import create_access_token
from app.services.s3_service import upload_image_to_s3
from app.core.security import create_access_token

router = APIRouter()

@router.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    # In a real application, you would integrate with an SMS gateway here (Twilio, AWS SNS, etc).
    # For now, we simulate sending a default OTP "1234"
    print(f"Sending mock OTP 1234 to {request.mobileNumber}")
    return {"message": "OTP sent successfully", "success": True}

@router.post("/register", response_model=Any)
async def register(
    shopName: str = Form(...),
    ownerName: str = Form(...),
    mobileNumber: str = Form(...),
    city: Optional[str] = Form(None),
    shopType: Optional[str] = Form(None),
    status: Optional[str] = Form("Active"),
    aadharCardFront: Optional[UploadFile] = File(None),
    aadharCardBack: Optional[UploadFile] = File(None)
):
    # 1. Check if customer already exists
    existing = await get_customer_by_mobile(mobileNumber)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this mobile number already exists")
        
    # 2. Handle image uploads via S3
    front_url = None
    back_url = None
    if aadharCardFront and getattr(aadharCardFront, 'filename', None):
        front_url = await upload_image_to_s3(aadharCardFront)
    if aadharCardBack and getattr(aadharCardBack, 'filename', None):
        back_url = await upload_image_to_s3(aadharCardBack)
    
    # 3. Create customer
    customer_in = CustomerCreate(
        shopName=shopName,
        ownerName=ownerName,
        mobileNumber=mobileNumber,
        city=city,
        shopType=shopType,
        status=status,
        aadharCardFront=front_url,
        aadharCardBack=back_url
    )
    customer = await create_customer(customer_in)
    
    # 4. Simulate sending OTP
    print(f"Sending mock OTP 1234 to {mobileNumber}")
    
    return {
        "message": "Details saved and OTP sent successfully",
        "success": True,
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

@router.put("/update/{customer_id}", response_model=Any)
async def update_profile(
    customer_id: str,
    shopName: Optional[str] = Form(None),
    ownerName: Optional[str] = Form(None),
    mobileNumber: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    shopType: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    aadharCardFront: Optional[UploadFile] = File(None),
    aadharCardBack: Optional[UploadFile] = File(None)
):
    # Verify customer exists
    existing = await get_customer(customer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    front_url = None
    back_url = None
    if aadharCardFront and getattr(aadharCardFront, 'filename', None):
        front_url = await upload_image_to_s3(aadharCardFront)
    if aadharCardBack and getattr(aadharCardBack, 'filename', None):
        back_url = await upload_image_to_s3(aadharCardBack)
        
    update_data = {}
    if shopName is not None: update_data["shopName"] = shopName
    if ownerName is not None: update_data["ownerName"] = ownerName
    if mobileNumber is not None: update_data["mobileNumber"] = mobileNumber
    if city is not None: update_data["city"] = city
    if shopType is not None: update_data["shopType"] = shopType
    if status is not None: update_data["status"] = status
    if front_url is not None: update_data["aadharCardFront"] = front_url
    if back_url is not None: update_data["aadharCardBack"] = back_url
        
    update_request = CustomerUpdate(**update_data)
    updated_customer = await update_customer(customer_id, update_request)
    
    return {
        "message": "Profile updated successfully",
        "customer": updated_customer
    }

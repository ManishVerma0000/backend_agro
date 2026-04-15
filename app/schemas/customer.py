from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CustomerAddressBase(BaseModel):
    location: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    shopName: Optional[str] = None
    ownerName: Optional[str] = None
    mobileNumber: Optional[str] = None
    nearbyLandmark: Optional[str] = None
    isDefault: Optional[bool] = False

class CustomerAddressCreate(CustomerAddressBase):
    pass

class CustomerAddressUpdate(BaseModel):
    location: Optional[str] = None
    shopName: Optional[str] = None
    ownerName: Optional[str] = None
    mobileNumber: Optional[str] = None
    nearbyLandmark: Optional[str] = None
    isDefault: Optional[bool] = None

class CustomerAddressResponse(CustomerAddressBase):
    id: str

class CustomerBase(BaseModel):
    shopName: str
    ownerName: str
    mobileNumber: str
    city: Optional[str] = None
    shopType: Optional[str] = None
    aadharCardFront: Optional[str] = None
    aadharCardBack: Optional[str] = None
    status: Optional[str] = "Active"
    
    # Analytics/Computed fields
    totalOrders: Optional[int] = 0
    totalSpent: Optional[float] = 0.0
    lastOrderDate: Optional[datetime] = None
    customerType: Optional[str] = "New"
    customerStatus: Optional[str] = "Active"

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    shopName: Optional[str] = None
    ownerName: Optional[str] = None
    mobileNumber: Optional[str] = None
    city: Optional[str] = None
    shopType: Optional[str] = None
    aadharCardFront: Optional[str] = None
    aadharCardBack: Optional[str] = None
    status: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: str
    createdDate: datetime
    
    model_config = ConfigDict(populate_by_name=True)

class SendOtpRequest(BaseModel):
    mobileNumber: str

class VerifyOtpRequest(BaseModel):
    mobileNumber: str
    otp: str

class RegisterRequest(CustomerBase):
    otp: str

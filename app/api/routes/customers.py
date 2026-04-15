from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerAddressCreate
from app.crud.customer import get_all_customers, create_customer, create_customer_address

router = APIRouter()

class AdminCustomerCreate(BaseModel):
    # Customer Fields
    shopName: str
    ownerName: str
    mobileNumber: str
    city: Optional[str] = None
    shopType: Optional[str] = None
    aadharCardFront: Optional[str] = None
    aadharCardBack: Optional[str] = None
    
    # Address Fields
    addressLocation: Optional[str] = None
    nearbyLandmark: Optional[str] = None
    isDefaultAddress: bool = True

@router.get("/", response_model=List[CustomerResponse])
async def read_customers():
    return await get_all_customers()

@router.post("/", response_model=CustomerResponse)
async def create_admin_customer(data: AdminCustomerCreate):
    # 1. Create the base customer
    cust_data = CustomerCreate(
        shopName=data.shopName,
        ownerName=data.ownerName,
        mobileNumber=data.mobileNumber,
        city=data.city,
        shopType=data.shopType,
        aadharCardFront=data.aadharCardFront,
        aadharCardBack=data.aadharCardBack,
        status="Active"
    )
    customer = await create_customer(cust_data)
    
    # 2. Add the address
    if data.addressLocation:
        addr_data = CustomerAddressCreate(
            location=data.addressLocation,
            shopName=data.shopName,
            ownerName=data.ownerName,
            mobileNumber=data.mobileNumber,
            nearbyLandmark=data.nearbyLandmark,
            isDefault=data.isDefaultAddress
        )
        await create_customer_address(customer["id"], addr_data)
        
    return customer

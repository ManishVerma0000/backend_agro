from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from typing import List, Optional
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerAddressCreate
from app.crud.customer import get_all_customers, create_customer, create_customer_address, get_customer_with_stats, get_customer_addresses
from app.utils.gmaps import resolve_google_maps_url
from app.services.s3_service import upload_image_to_s3

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def read_customers():
    return await get_all_customers()

@router.get("/detail/{id}", response_model=CustomerResponse)
async def read_customer(id: str):
    print(f"DEBUG: Fetching customer with ID: {id}")
    customer = await get_customer_with_stats(id)
    if not customer:
        print(f"DEBUG: Customer not found in DB: {id}")
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Enrichment with addresses
    customer["addresses"] = await get_customer_addresses(id)
    
    return customer

@router.post("/", response_model=CustomerResponse)
async def create_admin_customer(
    shopName: str = Form(...),
    ownerName: str = Form(...),
    mobileNumber: str = Form(...),
    city: Optional[str] = Form(None),
    shopType: Optional[str] = Form(None),
    aadharCardFront: Optional[UploadFile] = File(None),
    aadharCardBack: Optional[UploadFile] = File(None),
    addressLocation: Optional[str] = Form(None),
    nearbyLandmark: Optional[str] = Form(None),
    isDefaultAddress: bool = Form(True)
):
    # 1. Handle image uploads
    front_url = None
    back_url = None
    if aadharCardFront and getattr(aadharCardFront, 'filename', None):
        front_url = await upload_image_to_s3(aadharCardFront)
    if aadharCardBack and getattr(aadharCardBack, 'filename', None):
        back_url = await upload_image_to_s3(aadharCardBack)

    # 2. Create the base customer
    cust_data = CustomerCreate(
        shopName=shopName,
        ownerName=ownerName,
        mobileNumber=mobileNumber,
        city=city,
        shopType=shopType,
        aadharCardFront=front_url,
        aadharCardBack=back_url,
        status="Active"
    )
    customer = await create_customer(cust_data)
    
    # 3. Add the address
    if addressLocation:
        location_text = addressLocation
        lat = None
        long = None
        
        # Check if it's a Google Maps URL and resolve it
        if any(domain in location_text for domain in ["google.com/maps", "maps.app.goo.gl", "goo.gl/maps"]):
            details = await resolve_google_maps_url(location_text)
            if "error" not in details:
                # Use the resolved place name for clean display, keep URL as reference if name missing
                location_text = details.get("place_name") or location_text
                lat = details.get("lat")
                long = details.get("lng")
        
        addr_data = CustomerAddressCreate(
            location=location_text,
            lat=lat,
            long=long,
            shopName=shopName,
            ownerName=ownerName,
            mobileNumber=mobileNumber,
            nearbyLandmark=nearbyLandmark,
            isDefault=isDefaultAddress
        )
        await create_customer_address(customer["id"], addr_data)
        
    return await get_customer_with_stats(customer["id"])

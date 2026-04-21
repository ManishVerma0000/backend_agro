from fastapi import APIRouter, Depends, HTTPException
import httpx
import os
from typing import List
from dotenv import load_dotenv
from app.core.config import settings
from app.schemas.customer import CustomerAddressResponse, CustomerAddressCreate, CustomerAddressUpdate
from app.crud.customer import create_customer_address, get_customer_addresses, get_customer_address, update_customer_address, delete_customer_address
router = APIRouter()

load_dotenv()
google_map_key = os.getenv("GOOGLE_MAP_KEY")


@router.get("/", response_model=List[CustomerAddressResponse])
async def read_addresses(customer_id: str):
    return await get_customer_addresses(customer_id)

@router.post("/", response_model=CustomerAddressResponse)
async def create_address(address_in: CustomerAddressCreate, customer_id: str):
    return await create_customer_address(customer_id, address_in)

@router.put("/{id}", response_model=CustomerAddressResponse)
async def update_address(id: str, address_in: CustomerAddressUpdate, customer_id: str):
    # Verify ownership
    existing = await get_customer_address(id)
    if not existing or existing.get("customerId") != customer_id:
        raise HTTPException(status_code=404, detail="Address not found")
        
    updated = await update_customer_address(customer_id, id, address_in)
    return updated

@router.delete("/{id}")
async def delete_address(id: str):
    success = await delete_customer_address(id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted"}

@router.put("/{id}/default", response_model=CustomerAddressResponse)
async def set_default_address(id: str, customer_id: str):
    # Verify ownership
    existing = await get_customer_address(id)
    if not existing or existing.get("customerId") != customer_id:
        raise HTTPException(status_code=404, detail="Address not found")
        
    update_data = CustomerAddressUpdate(isDefault=True)
    updated = await update_customer_address(customer_id, id, update_data)
    return updated

@router.get("/geocode", response_model=dict)
async def get_address_from_lat_long(lat: float, long: float):
    if not google_map_key:
        raise HTTPException(status_code=500, detail="Google Map API key is not configured")
        
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{long}&key={google_map_key}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Google Maps API")
            
        data = response.json()
        # "ZERO_RESULTS" is possible but still 200 OK
        if data.get("status") == "ZERO_RESULTS":
            raise HTTPException(status_code=404, detail="No address found for these coordinates")
        elif data.get("status") != "OK":
            raise HTTPException(status_code=400, detail=f"Google Maps API Error: {data.get('status')}")
            
        results = data.get("results", [])
        if not results:
            raise HTTPException(status_code=404, detail="No results in data")
            
        formatted_address = results[0].get("formatted_address")
        
        return {
            "success": True,
            "address": formatted_address
        }

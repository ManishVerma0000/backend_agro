from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.customer import CustomerAddressResponse, CustomerAddressCreate, CustomerAddressUpdate
from app.crud.customer import create_customer_address, get_customer_addresses, get_customer_address, update_customer_address, delete_customer_address
router = APIRouter()

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
async def delete_address(id: str, customer_id: str):
    success = await delete_customer_address(customer_id, id)
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

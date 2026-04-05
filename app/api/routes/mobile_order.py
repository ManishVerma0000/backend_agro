from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.mobile_order import MobileOrderCreate, MobileOrderResponse
from app.crud.mobile_order import place_order, get_customer_orders

router = APIRouter()

@router.post("/", response_model=MobileOrderResponse)
async def create_order(order_in: MobileOrderCreate):
    try:
        return await place_order(order_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[MobileOrderResponse])
async def read_past_orders(customer_id: str = Query(...)):
    return await get_customer_orders(customer_id)

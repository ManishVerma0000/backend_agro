from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.crud import order as crud_order

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def read_orders():
    orders = await crud_order.get_orders()
    return orders

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate):
    order = await crud_order.create_order(order_in)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(order_id: str):
    order = await crud_order.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, order_in: OrderUpdate):
    order = await crud_order.update_order(order_id, order_in)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str):
    success = await crud_order.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")

from fastapi import APIRouter, HTTPException, Query
from typing import List, Any
from app.schemas.mobile_order import MobileOrderCreate, MobileOrderResponse
from app.crud.mobile_order import (
    place_order, get_customer_orders, get_warehouse_orders, 
    get_order_by_id, confirm_order, start_picking, 
    get_warehouse_orders_by_status, start_packing, ready_for_dispatch, delete_order
)

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

# Specific warehouse routes MUST come before /{order_id} to avoid path conflicts
@router.get("/warehouse/{warehouse_id}/by-status")
async def read_orders_by_status(warehouse_id: str, status: str = Query(...)):
    orders = await get_warehouse_orders_by_status(warehouse_id, status)
    return orders

@router.get("/warehouse/{warehouse_id}")
async def read_warehouse_orders(warehouse_id: str):
    return await get_warehouse_orders(warehouse_id)

@router.get("/{order_id}")
async def read_order(order_id: str):
    order = await get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}")
async def remove_order(order_id: str):
    success = await delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

@router.patch("/{order_id}/confirm")
async def confirm_order_status(order_id: str):
    order = await confirm_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{order_id}/start-picking")
async def start_picking_status(order_id: str):
    order = await start_picking(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{order_id}/start-packing")
async def start_packing_status(order_id: str):
    order = await start_packing(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{order_id}/ready-for-dispatch")
async def ready_for_dispatch_status(order_id: str):
    order = await ready_for_dispatch(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

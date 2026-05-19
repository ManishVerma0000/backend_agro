from fastapi import APIRouter, HTTPException, Query
from typing import List, Any, Optional
from app.schemas.mobile_order import MobileOrderCreate, MobileOrderResponse, MobileOrderListResponse, MobileOrderUpdatePaymentStatus, MobileOrderBulkUpdateStatus
from app.crud.mobile_order import (
    place_order, get_customer_orders, get_warehouse_orders, 
    get_order_by_id, confirm_order, start_picking, 
    get_warehouse_orders_by_status, start_packing, ready_for_dispatch, delete_order,
    update_payment_status, bulk_update_status
)

router = APIRouter()

@router.post("/", response_model=MobileOrderResponse)
async def create_order(order_in: MobileOrderCreate):
    try:
        return await place_order(order_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=MobileOrderListResponse)
async def read_past_orders(
    customer_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    days: Optional[int] = Query(None, ge=1)
):
    return await get_customer_orders(customer_id, skip, limit, days)

# Specific warehouse routes MUST come before /{order_id} to avoid path conflicts
@router.get("/warehouse/{warehouse_id}/by-status")
async def read_orders_by_status(warehouse_id: str, status: str = Query(...)):
    orders = await get_warehouse_orders_by_status(warehouse_id, status)
    return orders

@router.get("/warehouse/{warehouse_id}")
async def read_warehouse_orders(
    warehouse_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return await get_warehouse_orders(warehouse_id, skip, limit)

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
    try:
        order = await start_packing(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{order_id}/ready-for-dispatch")
async def ready_for_dispatch_status(order_id: str):
    order = await ready_for_dispatch(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
@router.patch("/{order_id}/payment-status")
async def update_payment_status_route(order_id: str, payment_in: MobileOrderUpdatePaymentStatus):
    order = await update_payment_status(order_id, payment_in.paymentStatus)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
@router.post("/bulk-update-status")
async def bulk_update_order_status(bulk_in: MobileOrderBulkUpdateStatus):
    success = await bulk_update_status(bulk_in.orderIds, bulk_in.status)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update some or all orders")
    return {"message": "Orders updated successfully"}

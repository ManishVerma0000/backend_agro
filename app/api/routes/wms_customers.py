from fastapi import APIRouter, HTTPException
from typing import List
from app.crud.wms_customer import get_customers_by_warehouse

router = APIRouter()


@router.get("/warehouse/{warehouse_id}")
async def read_warehouse_customers(warehouse_id: str):
    """
    Returns all customers who have ordered from a specific warehouse,
    enriched with order stats (total orders, total spent, last order date).
    """
    customers = await get_customers_by_warehouse(warehouse_id)
    return customers

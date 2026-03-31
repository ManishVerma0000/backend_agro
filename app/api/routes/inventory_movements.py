from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.inventory_movement import InventoryMovementResponse
from app.crud.inventory_movement import get_inventory_movements

router = APIRouter()

@router.get("/", response_model=List[InventoryMovementResponse])
async def read_inventory_movements(warehouse_id: Optional[str] = Query(None)):
    """
    Retrieve inventory movements.
    """
    movements = await get_inventory_movements(warehouse_id=warehouse_id)
    return movements

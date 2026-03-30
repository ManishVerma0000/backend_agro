from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.inventory import InventoryMovementCreate, InventoryMovementUpdate, InventoryMovementResponse
from app.crud import inventory as crud_inventory

router = APIRouter()

@router.get("/movements", response_model=List[InventoryMovementResponse])
async def read_movements():
    return await crud_inventory.get_movements()

@router.post("/movements", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(movement_in: InventoryMovementCreate):
    return await crud_inventory.create_movement(movement_in)

@router.get("/movements/{movement_id}", response_model=InventoryMovementResponse)
async def read_movement(movement_id: str):
    m = await crud_inventory.get_movement(movement_id)
    if not m:
        raise HTTPException(status_code=404, detail="Movement not found")
    return m

@router.put("/movements/{movement_id}", response_model=InventoryMovementResponse)
async def update_movement(movement_id: str, movement_in: InventoryMovementUpdate):
    m = await crud_inventory.update_movement(movement_id, movement_in)
    if not m:
        raise HTTPException(status_code=404, detail="Movement not found")
    return m

@router.delete("/movements/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement(movement_id: str):
    success = await crud_inventory.delete_movement(movement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movement not found")

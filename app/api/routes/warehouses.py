from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.crud import warehouse as crud_warehouse

router = APIRouter()

@router.get("/", response_model=List[WarehouseResponse])
async def read_warehouses():
    warehouses = await crud_warehouse.get_warehouses()
    return warehouses

@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(warehouse_in: WarehouseCreate):
    warehouse = await crud_warehouse.create_warehouse(warehouse_in)
    return warehouse

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def read_warehouse(warehouse_id: str):
    warehouse = await crud_warehouse.get_warehouse(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(warehouse_id: str, warehouse_in: WarehouseUpdate):
    warehouse = await crud_warehouse.update_warehouse(warehouse_id, warehouse_in)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: str):
    success = await crud_warehouse.delete_warehouse(warehouse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse not found")

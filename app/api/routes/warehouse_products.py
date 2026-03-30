from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional
from app.schemas.warehouse_product import WarehouseProductCreate, WarehouseProductUpdate, WarehouseProductResponse
from app.crud.warehouse_product import (
    get_warehouse_products,
    get_warehouse_product,
    create_warehouse_product,
    update_warehouse_product,
    delete_warehouse_product
)

router = APIRouter()

@router.get("/", response_model=List[WarehouseProductResponse])
async def read_warehouse_products(warehouse_id: Optional[str] = None):
    return await get_warehouse_products(warehouse_id)

@router.post("/", response_model=WarehouseProductResponse)
async def create_warehouse_product_endpoint(product_in: WarehouseProductCreate):
    return await create_warehouse_product(product_in)

@router.get("/{id}", response_model=WarehouseProductResponse)
async def read_warehouse_product(id: str = Path(...)):
    product = await get_warehouse_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Warehouse product not found")
    return product

@router.put("/{id}", response_model=WarehouseProductResponse)
async def update_warehouse_product_endpoint(id: str, product_in: WarehouseProductUpdate):
    product = await update_warehouse_product(id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Warehouse product not found")
    return product

@router.delete("/{id}")
async def delete_warehouse_product_endpoint(id: str):
    success = await delete_warehouse_product(id)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse product not found")
    return {"message": "Warehouse product deleted successfully"}

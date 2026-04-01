from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from app.schemas.mobile import MobileProductResponse, MobileHomeResponse
from app.crud.mobile import get_mobile_home, get_mobile_products

router = APIRouter()

@router.get("/home", response_model=MobileHomeResponse)
async def read_mobile_home(warehouse_id: str = Query(...)):
    return await get_mobile_home(warehouse_id)

@router.get("/products", response_model=List[MobileProductResponse])
async def read_mobile_products(
    warehouse_id: str = Query(...), 
    category_id: Optional[str] = Query(None)
):
    return await get_mobile_products(warehouse_id, category_id)

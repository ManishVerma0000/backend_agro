from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from app.schemas.mobile import MobileProductResponse, MobileHomeResponse, MobileCategoryFull
from app.crud.mobile import get_mobile_home, get_mobile_products, get_mobile_categories

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

@router.get("/categories", response_model=List[MobileCategoryFull])
async def read_mobile_categories():
    return await get_mobile_categories()

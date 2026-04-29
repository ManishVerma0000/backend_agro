from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from app.schemas.mobile import MobileProductResponse, MobileHomeResponse, MobileCategoryFull, MobileCategoryWithProducts
from app.crud.mobile import get_mobile_home, get_mobile_products, get_mobile_categories, get_categories_with_products
from app.services.offer_logic import get_applicable_offer

router = APIRouter()

@router.get("/home", response_model=MobileHomeResponse)
async def read_mobile_home(
    warehouse_id: str = Query(...),
    customer_id: Optional[str] = Query(None)
):
    return await get_mobile_home(warehouse_id, customer_id)

@router.get("/products", response_model=List[MobileProductResponse])
async def read_mobile_products(
    warehouse_id: str = Query(...), 
    category_id: Optional[str] = Query(None),
    subcategory_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    # Handle Javascript "undefined" being passed as a string
    if category_id == "undefined":
        category_id = None
    if subcategory_id == "undefined":
        subcategory_id = None
    if search == "undefined":
        search = None
        
    return await get_mobile_products(warehouse_id, category_id, subcategory_id, search)

@router.get("/products/{product_id}", response_model=MobileProductResponse)
async def read_mobile_product_details(
    product_id: str,
    warehouse_id: str = Query(...)
):
    from fastapi import HTTPException
    from app.crud.mobile import get_mobile_product_details
    product = await get_mobile_product_details(warehouse_id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in warehouse")
    return product

@router.get("/categories", response_model=List[MobileCategoryFull])
async def read_mobile_categories():
    return await get_mobile_categories()

@router.get("/categories-with-products", response_model=List[MobileCategoryWithProducts])
async def read_categories_with_products(warehouse_id: str = Query(...)):
    return await get_categories_with_products(warehouse_id)

@router.get("/offers")
async def read_mobile_offers(customer_id: str = Query(...), cart_value: float = Query(0)):
    offer = await get_applicable_offer(customer_id, cart_value)
    return {"offer": offer}

@router.get("/nearest-warehouse")
async def read_nearest_warehouse(lat: float = Query(...), lon: float = Query(...)):
    from app.crud.mobile import get_nearest_warehouse
    warehouse = await get_nearest_warehouse(lat, lon)
    if not warehouse:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No active warehouse found near this location")
    return warehouse

@router.get("/today-price-list")
async def read_today_price_list(
    warehouse_id: str = Query(...),
    customer_id: Optional[str] = Query(None)
):
    from app.crud.mobile import get_today_price_list
    return await get_today_price_list(warehouse_id, customer_id)

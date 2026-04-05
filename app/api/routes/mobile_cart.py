from fastapi import APIRouter, HTTPException, Query
from app.schemas.mobile_cart import MobileCartItemCreate, MobileCartItemUpdate, MobileCartResponse, MobileCartItemResponse
from app.crud.mobile_cart import add_to_cart, get_active_cart, remove_from_cart, update_cart_item

router = APIRouter()

@router.post("/", response_model=MobileCartItemResponse)
async def create_cart_item(item_in: MobileCartItemCreate):
    return await add_to_cart(item_in)

@router.get("/", response_model=MobileCartResponse)
async def read_active_cart(
    customer_id: str = Query(...), 
    warehouse_id: str = Query(...)
):
    return await get_active_cart(customer_id, warehouse_id)

@router.put("/{item_id}", response_model=MobileCartItemResponse)
async def modify_cart_item(item_id: str, item_in: MobileCartItemUpdate):
    item = await update_cart_item(item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return item

@router.delete("/{item_id}")
async def delete_cart_item(item_id: str):
    success = await remove_from_cart(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

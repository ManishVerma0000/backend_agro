from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.db.session import get_db
from app.schemas.mobile_order import MobileOrderCreate
from app.crud.mobile_cart import get_active_cart

async def place_order(order_in: MobileOrderCreate) -> dict:
    db = get_db()
    
    # 1. Fetch the active cart to get items and totals
    cart_data = await get_active_cart(order_in.customerId, order_in.warehouseId)
    
    if not cart_data["items"]:
        raise ValueError("Cannot place an order with an empty cart")
        
    items = cart_data["items"]
    item_ids = [ObjectId(item["id"]) for item in items]
    
    # 2. Construct the Order payload
    order_dict = order_in.model_dump()
    order_dict["subtotal"] = cart_data["subtotal"]
    order_dict["deliveryFee"] = cart_data["deliveryFee"]
    order_dict["grandTotal"] = cart_data["grandTotal"]
    order_dict["status"] = "Placed"
    order_dict["createdAt"] = datetime.utcnow()
    
    # Store the actual cart items inside the order snapshot so history doesn't break if cart item changes
    order_dict["items"] = items 
    
    # 3. Insert the order
    result = await db["mobile_orders"].insert_one(order_dict)
    
    # 4. Update the cart items to mark them as `is_order_place = True`
    await db["cart_items"].update_many(
        {"_id": {"$in": item_ids}},
        {"$set": {"is_order_place": True, "orderId": str(result.inserted_id)}}
    )
    
    # 5. Inventory deduction (optional based on your inventory strategy, we'll leave it simple for now)
    # usually here we would reduce `availableStock` on `warehouse_products`
    
    return await get_order(str(result.inserted_id))


async def get_order(order_id: str) -> Optional[dict]:
    db = get_db()
    order = await db["mobile_orders"].find_one({"_id": ObjectId(order_id)})
    if order:
        order["id"] = str(order.pop("_id"))
    return order


async def get_customer_orders(customer_id: str) -> List[dict]:
    db = get_db()
    cursor = db["mobile_orders"].find({"customerId": customer_id}).sort("createdAt", -1)
    orders = []
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        orders.append(order)
    return orders

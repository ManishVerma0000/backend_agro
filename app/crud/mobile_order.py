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

async def get_warehouse_orders(warehouse_id: str) -> List[dict]:
    db = get_db()
    pipeline = [
        {"$match": {"warehouseId": warehouse_id}},
        {
            "$addFields": {
                "customerObjectId": {"$toObjectId": "$customerId"}
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerObjectId",
                "foreignField": "_id",
                "as": "customer_info"
            }
        },
        {"$unwind": {"path": "$customer_info", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "customerName": {"$ifNull": ["$customer_info.shopName", "$customer_info.ownerName", "Unknown Customer"]},
                "location": {"$ifNull": ["$customer_info.city", "Unknown Location"]}
            }
        },
        {"$sort": {"createdAt": -1}},
        {"$project": {"customer_info": 0, "customerObjectId": 0}}
    ]
    
    cursor = db["mobile_orders"].aggregate(pipeline)
    orders = []
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        orders.append(order)
    return orders

async def get_order_by_id(order_id: str) -> Optional[dict]:
    db = get_db()
    
    try:
        obj_id = ObjectId(order_id)
    except:
        return None
        
    pipeline = [
        {"$match": {"_id": obj_id}},
        {
            "$addFields": {
                "customerObjectId": {"$toObjectId": "$customerId"},
                "addressObjectId": {"$toObjectId": "$deliveryAddressId"}
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerObjectId",
                "foreignField": "_id",
                "as": "customer_info"
            }
        },
        {"$unwind": {"path": "$customer_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "customer_addresses",
                "localField": "addressObjectId",
                "foreignField": "_id",
                "as": "address_info"
            }
        },
        {"$unwind": {"path": "$address_info", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "customerName": {"$ifNull": ["$customer_info.shopName", "$customer_info.ownerName", "Unknown Customer"]},
                "customerPhone": {"$ifNull": ["$customer_info.mobileNumber", "Unknown Phone"]},
                "customerEmail": {"$ifNull": ["$customer_info.email", "N/A"]},
                "location": {
                    "$cond": [
                        {"$ne": ["$address_info", None]},
                        {"$concat": [
                            {"$ifNull": ["$address_info.shopName", ""]}, ", ",
                            {"$ifNull": ["$address_info.location", ""]}
                        ]},
                        {"$ifNull": ["$customer_info.city", "Unknown Location"]}
                    ]
                }
            }
        },
        {"$project": {"customer_info": 0, "customerObjectId": 0, "address_info": 0, "addressObjectId": 0}}
    ]
    
    cursor = db["mobile_orders"].aggregate(pipeline)
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        return order
        
    return None


async def confirm_order(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None
    
    result = await db["mobile_orders"].update_one(
        {"_id": obj_id},
        {"$set": {"status": "Confirmed"}}
    )
    
    if result.matched_count == 0:
        return None
    
    return await get_order_by_id(order_id)


async def start_picking(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None
    
    result = await db["mobile_orders"].update_one(
        {"_id": obj_id},
        {"$set": {"status": "Picking"}}
    )
    
    if result.matched_count == 0:
        return None
    
    return await get_order_by_id(order_id)


async def get_warehouse_orders_by_status(warehouse_id: str, status: str) -> List[dict]:
    db = get_db()
    pipeline = [
        {"$match": {"warehouseId": warehouse_id, "status": status}},
        {
            "$addFields": {
                "customerObjectId": {"$toObjectId": "$customerId"}
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerObjectId",
                "foreignField": "_id",
                "as": "customer_info"
            }
        },
        {"$unwind": {"path": "$customer_info", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "customerName": {"$ifNull": ["$customer_info.shopName", "$customer_info.ownerName", "Unknown Customer"]},
                "location": {"$ifNull": ["$customer_info.city", "Unknown Location"]}
            }
        },
        {"$sort": {"createdAt": -1}},
        {"$project": {"customer_info": 0, "customerObjectId": 0}}
    ]
    
    cursor = db["mobile_orders"].aggregate(pipeline)
    orders = []
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        orders.append(order)
    return orders


async def start_packing(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None

    result = await db["mobile_orders"].update_one(
        {"_id": obj_id},
        {"$set": {"status": "Packing"}}
    )

    if result.matched_count == 0:
        return None

    return await get_order_by_id(order_id)


async def ready_for_dispatch(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None

    result = await db["mobile_orders"].update_one(
        {"_id": obj_id},
        {"$set": {"status": "Ready for Dispatch"}}
    )

    if result.matched_count == 0:
        return None

    return await get_order_by_id(order_id)

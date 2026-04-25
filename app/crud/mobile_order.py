from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.db.session import get_db
from app.schemas.mobile_order import MobileOrderCreate
from app.crud.mobile_cart import get_active_cart

async def place_order(order_in: MobileOrderCreate) -> dict:
    db = get_db()
    order_dict = order_in.model_dump(exclude_unset=True)
    
    # Unify items from either 'items' (admin) or 'cartItems' (mobile)
    items = order_in.cartItems if order_in.cartItems is not None else order_in.items
    
    if not items:
        raise ValueError("Cannot place an order without items")

    # Handle mobile address object if provided
    if order_in.address and isinstance(order_in.address, dict):
        order_dict["deliveryAddress"] = order_in.address
        if "id" in order_in.address:
            order_dict["deliveryAddressId"] = order_in.address["id"]

    # Clean up redundant keys
    order_dict.pop("cartItems", None)
    order_dict.pop("address", None)
    
    order_dict["subtotal"] = order_in.subtotal or 0
    order_dict["deliveryFee"] = order_in.deliveryFee or 0
    order_dict["grandTotal"] = order_in.grandTotal or 0
    order_dict["status"] = "Placed"
    order_dict["createdAt"] = datetime.utcnow()
    order_dict["items"] = items 
    
    result = await db["mobile_orders"].insert_one(order_dict)
    
    # Record offer usage if present
    if order_in.offerId:
        await db["offer_usage"].insert_one({
            "offerId": order_in.offerId,
            "customerId": order_in.customerId,
            "orderId": str(result.inserted_id),
            "createdAt": datetime.utcnow()
        })
    
    return await get_order(str(result.inserted_id))

async def delete_order(order_id: str) -> bool:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return False
        
    result = await db["mobile_orders"].delete_one({"_id": obj_id})
    return result.deleted_count > 0


async def get_order(order_id: str) -> Optional[dict]:
    db = get_db()
    order = await db["mobile_orders"].find_one({"_id": ObjectId(order_id)})
    if order:
        order["id"] = str(order.pop("_id"))
    return order


async def get_customer_orders(customer_id: str, skip: int = 0, limit: int = 20) -> dict:
    db = get_db()
    total = await db["mobile_orders"].count_documents({"customerId": customer_id})
    cursor = db["mobile_orders"].find({"customerId": customer_id}).sort("createdAt", -1).skip(skip).limit(limit)
    orders = []
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        orders.append(order)
    return {
        "items": orders,
        "total": total,
        "skip": skip,
        "limit": limit
    }

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
                "customerPhone": {"$ifNull": ["$customer_info.mobileNumber", "N/A"]},
                "customerEmail": {"$ifNull": ["$customer_info.email", "N/A"]},
                "location": {
                    "$ifNull": [
                        "$deliveryAddress.location",
                        "$deliveryAddress.city",
                        "$customer_info.city",
                        "Unknown Location"
                    ]
                }
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
                "customerPhone": {"$ifNull": ["$customer_info.mobileNumber", "N/A"]},
                "customerEmail": {"$ifNull": ["$customer_info.email", "N/A"]},
                "location": {
                    "$ifNull": [
                        "$deliveryAddress.location",
                        "$deliveryAddress.city",
                        "$customer_info.city",
                        "Unknown Location"
                    ]
                }
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

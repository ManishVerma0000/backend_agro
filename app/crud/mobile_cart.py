from typing import List, Optional, Dict
from bson import ObjectId
from app.db.session import get_db
from app.schemas.mobile_cart import MobileCartItemCreate, MobileCartItemUpdate, MobileCartBulkUpdate

async def bulk_add_to_cart(bulk_in: MobileCartBulkUpdate) -> dict:
    db = get_db()
    
    for item in bulk_in.items:
        product_id = item.get("productId")
        quantity = item.get("quantity", 0)
        
        if not product_id or quantity <= 0:
            continue
            
        # Check if this item is already in the active cart
        existing_item = await db["cart_items"].find_one({
            "customerId": bulk_in.customerId,
            "warehouseId": bulk_in.warehouseId,
            "productId": product_id,
            "is_order_place": False,
            "is_item_removed": {"$ne": True}
        })
        
        if existing_item:
            # Update quantity (usually bulk means setting current state, but we'll assume adding here)
            # Actually, for mobile sync, it might mean "set quantity to X"
            # Let's assume ADDING for now, unless the user clarifies.
            new_quantity = existing_item.get("quantity", 0) + quantity
            await db["cart_items"].update_one(
                {"_id": existing_item["_id"]},
                {"$set": {"quantity": new_quantity, "is_item_added_cart": True}}
            )
        else:
            # Create new
            item_dict = {
                "customerId": bulk_in.customerId,
                "warehouseId": bulk_in.warehouseId,
                "productId": product_id,
                "quantity": quantity,
                "is_item_added_cart": True,
                "is_order_place": False,
                "is_item_removed": False
            }
            await db["cart_items"].insert_one(item_dict)
            
    return await get_active_cart(bulk_in.customerId, bulk_in.warehouseId)

async def add_to_cart(item_in: MobileCartItemCreate) -> dict:
    db = get_db()
    
    # Check if this item is already in the active cart
    existing_item = await db["cart_items"].find_one({
        "customerId": item_in.customerId,
        "warehouseId": item_in.warehouseId,
        "productId": item_in.productId,
        "is_order_place": False,
        "is_item_removed": {"$ne": True}
    })
    
    if existing_item:
        # Increment quantity
        new_quantity = existing_item.get("quantity", 0) + item_in.quantity
        await db["cart_items"].update_one(
            {"_id": existing_item["_id"]},
            {"$set": {"quantity": new_quantity, "is_item_added_cart": True}}
        )
        return await get_cart_item(str(existing_item["_id"]))
    
    # Otherwise create new
    item_dict = item_in.model_dump()
    item_dict["is_item_added_cart"] = True
    item_dict["is_order_place"] = False
    item_dict["is_item_removed"] = False
    
    result = await db["cart_items"].insert_one(item_dict)
    return await get_cart_item(str(result.inserted_id))


async def update_cart_item(item_id: str, item_in: MobileCartItemUpdate) -> Optional[dict]:
    db = get_db()
    await db["cart_items"].update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"quantity": item_in.quantity}}
    )
    return await get_cart_item(item_id)


async def remove_from_cart(item_id: str) -> bool:
    db = get_db()
    # Soft delete
    result = await db["cart_items"].update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {
            "is_item_added_cart": None,
            "is_item_removed": True
        }}
    )
    return result.modified_count > 0


async def get_cart_item(item_id: str) -> Optional[dict]:
    db = get_db()
    item = await db["cart_items"].find_one({"_id": ObjectId(item_id)})
    if item:
        item["id"] = str(item.pop("_id"))
    return item


async def get_active_cart(customer_id: str, warehouse_id: str) -> Dict:
    db = get_db()
    
    match_query = {
        "customerId": customer_id,
        "warehouseId": warehouse_id,
        "is_order_place": False,
        "is_item_removed": {"$ne": True}
    }
    
    pipeline = [
        {"$match": match_query},
        {"$addFields": {"productObjectId": {"$toObjectId": "$productId"}}},
        {
            "$lookup": {
                "from": "products",
                "localField": "productObjectId",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "warehouse_products",
                "let": {"pid": "$productId", "wid": "$warehouseId"},
                "pipeline": [
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$productId", "$$pid"]},
                                {"$eq": ["$warehouseId", "$$wid"]}
                            ]
                        }
                    }}
                ],
                "as": "warehouse_product_info"
            }
        },
        {"$unwind": {"path": "$warehouse_product_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 1,
                "customerId": 1,
                "warehouseId": 1,
                "productId": 1,
                "quantity": 1,
                "is_item_added_cart": 1,
                "is_order_place": 1,
                "is_item_removed": 1,
                "productDetails": {
                    "name": "$product_info.name",
                    "imageUrl": "$product_info.imageUrl",
                    "baseUnit": "$product_info.baseUnit",
                    "basePrice": {
                        "$cond": [
                            {"$and": [{"$ne": ["$warehouse_product_info.basePrice", None]}, {"$gt": ["$warehouse_product_info.basePrice", 0]}]},
                            "$warehouse_product_info.basePrice", 
                            {"$toDouble": "$product_info.basePrice"}
                        ]
                    },
                    "mrp": "$product_info.mrp",
                    "status": "$warehouse_product_info.status",
                    "availableStock": "$warehouse_product_info.availableStock"
                }
            }
        }
    ]
    
    cursor = db["cart_items"].aggregate(pipeline)
    items = []
    subtotal = 0.0
    
    async for item in cursor:
        item["id"] = str(item.pop("_id"))
        quantity = item.get("quantity", 0)
        base_price = item.get("productDetails", {}).get("basePrice", 0)
        try:
            subtotal += (float(base_price) * quantity)
        except:
            pass
        items.append(item)
        
    delivery_fee = 0.0 if subtotal > 500 else 50.0  # Simple logic: free delivery over 500
    if len(items) == 0:
        delivery_fee = 0.0
        
    grand_total = subtotal + delivery_fee
    
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "deliveryFee": round(delivery_fee, 2),
        "grandTotal": round(grand_total, 2)
    }

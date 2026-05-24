from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from app.db.session import get_db
from app.schemas.mobile_order import MobileOrderCreate
from app.crud.mobile_cart import get_active_cart

async def reserve_order_stock(order_id: str, db) -> None:
    order = await db["mobile_orders"].find_one({"_id": ObjectId(order_id)})
    if not order:
        return
        
    warehouse_id = order.get("warehouseId")
    if not warehouse_id:
        return
        
    items = order.get("items", []) or order.get("cartItems", [])
    for item in items:
        product_id = item.get("productId")
        qty = item.get("quantity", 0)
        if not product_id or qty <= 0:
            continue
            
        wp = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
        if wp:
            await db["warehouse_products"].update_one(
                {"_id": wp["_id"]},
                {
                    "$inc": {
                        "reservedStock": qty,
                        "availableStock": -qty
                    }
                }
            )
        else:
            prod_details = await db["products"].find_one({"_id": ObjectId(product_id)})
            image_url = prod_details.get("imageUrl") if prod_details else None
            
            from app.schemas.warehouse_product import WarehouseProductCreate
            wp_create = WarehouseProductCreate(
                productId=product_id,
                warehouseId=warehouse_id,
                initialStock=0,
                currentStock=0,
                reservedStock=qty,
                availableStock=-qty,
                basePrice=item.get("unitPrice") or 0.0,
                imageUrl=image_url
            )
            await db["warehouse_products"].insert_one(wp_create.model_dump())

async def update_order_status_in_db(order_id: str, new_status: str, db) -> None:
    order = await db["mobile_orders"].find_one({"_id": ObjectId(order_id)})
    if not order:
        return
        
    prev_status = order.get("status")
    
    if prev_status == new_status:
        return
        
    await db["mobile_orders"].update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}}
    )
    
    if new_status == "Delivered":
        dispatch_id = order.get("dispatchId")
        if dispatch_id:
            try:
                total_in_dispatch = await db["mobile_orders"].count_documents({"dispatchId": dispatch_id})
                delivered_in_dispatch = await db["mobile_orders"].count_documents({"dispatchId": dispatch_id, "status": "Delivered"})
                if total_in_dispatch > 0 and total_in_dispatch == delivered_in_dispatch:
                    await db["dispatches"].update_one(
                        {"_id": ObjectId(dispatch_id)},
                        {"$set": {"status": "Delivered"}}
                    )
            except Exception as ex:
                print(f"Error checking dispatch delivery status for batch {dispatch_id}: {ex}")
    
    if new_status == "Out for Delivery" and not order.get("stockReduced"):
        warehouse_id = order.get("warehouseId")
        items = order.get("items", []) or order.get("cartItems", [])
        
        for item in items:
            product_id = item.get("productId")
            qty = item.get("quantity", 0)
            if not product_id or qty <= 0:
                continue
                
            wp = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
            if wp:
                prev_stock = wp.get("currentStock", 0)
                new_stock = prev_stock - qty
                
                await db["warehouse_products"].update_one(
                    {"_id": wp["_id"]},
                    {
                        "$inc": {
                            "currentStock": -qty,
                            "reservedStock": -qty
                        }
                    }
                )
            else:
                prev_stock = 0
                new_stock = -qty
                
            from app.schemas.inventory_movement import InventoryMovementCreate
            from app.crud.inventory_movement import log_movement
            
            movement = InventoryMovementCreate(
                productId=product_id,
                warehouseId=warehouse_id,
                type="Order Fulfillment",
                quantity=-qty,
                prevStock=prev_stock,
                newStock=new_stock,
                reference=f"Order Dispatched: {order.get('orderNumber') or order.get('id')}",
                user="System",
                date=datetime.utcnow()
            )
            await log_movement(movement)
            
        await db["mobile_orders"].update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"stockReduced": True}}
        )

async def resolve_closest_warehouse_id(address: dict) -> Optional[str]:
    if not address or not isinstance(address, dict):
        return None
    lat_val = address.get("lat")
    lon_val = address.get("long") or address.get("lon") or address.get("lng")
    if lat_val is not None and lon_val is not None:
        try:
            lat_f = float(lat_val)
            lon_f = float(lon_val)
            from app.crud.mobile import get_nearest_warehouse
            nearest = await get_nearest_warehouse(lat_f, lon_f)
            if nearest:
                return nearest["id"]
        except Exception as e:
            print(f"Error resolving closest warehouse: {e}")
    return None

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
            
        # Dynamically resolve closest warehouse ID based on address coordinates
        resolved_wh_id = await resolve_closest_warehouse_id(order_in.address)
        if resolved_wh_id:
            order_dict["warehouseId"] = resolved_wh_id
 
    # Clean up redundant keys
    order_dict.pop("cartItems", None)
    order_dict.pop("address", None)
    
    order_dict["subtotal"] = order_in.subtotal or 0
    order_dict["deliveryFee"] = order_in.deliveryFee or 0
    order_dict["grandTotal"] = order_in.grandTotal or 0
    order_dict["status"] = "Placed"
    order_dict["createdAt"] = datetime.utcnow()
    order_dict["items"] = items 
    if "paymentStatus" not in order_dict:
        order_dict["paymentStatus"] = None
    
    result = await db["mobile_orders"].insert_one(order_dict)
    
    # Reserve stock for the order
    await reserve_order_stock(str(result.inserted_id), db)
    
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
        
        # Dynamically resolve closest warehouse ID if coordinates exist
        addr = order.get("deliveryAddress")
        resolved_wh_id = await resolve_closest_warehouse_id(addr)
        if resolved_wh_id:
            order["warehouseId"] = resolved_wh_id
            
    return order


async def get_customer_orders(customer_id: str, skip: int = 0, limit: int = 20, days: Optional[int] = None) -> dict:
    db = get_db()
    query = {"customerId": customer_id}
    
    if days is not None:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query["createdAt"] = {"$gte": date_threshold}
        
    total = await db["mobile_orders"].count_documents(query)
    cursor = db["mobile_orders"].find(query).sort("createdAt", -1).skip(skip).limit(limit)
    orders = []
    async for order in cursor:
        order["id"] = str(order.pop("_id"))
        
        # Dynamically resolve closest warehouse ID if coordinates exist
        addr = order.get("deliveryAddress")
        resolved_wh_id = await resolve_closest_warehouse_id(addr)
        if resolved_wh_id:
            order["warehouseId"] = resolved_wh_id
            
        orders.append(order)
    return {
        "items": orders,
        "total": total,
        "skip": skip,
        "limit": limit
    }

async def get_warehouse_orders(warehouse_id: str, skip: int = 0, limit: int = 10) -> dict:
    db = get_db()
    
    # Count total first
    total = await db["mobile_orders"].count_documents({"warehouseId": warehouse_id})
    
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
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {"customer_info": 0, "customerObjectId": 0}}
    ]
    
    cursor = db["mobile_orders"].aggregate(pipeline)
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
        
        # Dynamically resolve closest warehouse ID if coordinates exist
        addr = order.get("deliveryAddress")
        resolved_wh_id = await resolve_closest_warehouse_id(addr)
        if resolved_wh_id:
            order["warehouseId"] = resolved_wh_id
            
        return order
        
    return None


async def confirm_order(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None
    
    await update_order_status_in_db(order_id, "Confirmed", db)
    return await get_order_by_id(order_id)


async def start_picking(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None
    
    await update_order_status_in_db(order_id, "Picking", db)
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

    order = await db["mobile_orders"].find_one({"_id": obj_id})
    if not order:
        return None
        
    warehouse_id = order.get("warehouseId")
    items = order.get("items", []) or order.get("cartItems", [])
    
    for item in items:
        product_id = item.get("productId")
        qty = item.get("quantity", 0)
        if not product_id or qty <= 0:
            continue
            
        wp = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
        
        # If no record exists, or if availableStock < 0 (reservation deficit), or if currentStock < qty (physical deficit)
        if not wp or wp.get("availableStock", 0) < 0 or wp.get("currentStock", 0) < qty:
            raise ValueError("Items stock is not available or partially available")

    await update_order_status_in_db(order_id, "Packing", db)
    return await get_order_by_id(order_id)


async def ready_for_dispatch(order_id: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None

    await update_order_status_in_db(order_id, "Ready for Dispatch", db)
    return await get_order_by_id(order_id)

async def update_payment_status(order_id: str, payment_status: str) -> Optional[dict]:
    db = get_db()
    try:
        obj_id = ObjectId(order_id)
    except:
        return None

    result = await db["mobile_orders"].update_one(
        {"_id": obj_id},
        {"$set": {"paymentStatus": payment_status}}
    )

    if result.matched_count == 0:
        return None

    return await get_order_by_id(order_id)

async def bulk_update_status(order_ids: List[str], status: str) -> bool:
    db = get_db()
    for oid in order_ids:
        try:
            await update_order_status_in_db(oid, status, db)
        except Exception as e:
            print(f"Error bulk updating order {oid}: {e}")
    return True

from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.procurement import SupplierCreate, SupplierUpdate, PurchaseOrderCreate, PurchaseOrderUpdate

# Suppliers
async def get_suppliers(warehouse_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    
    match_stage = {}
    if warehouse_id and warehouse_id not in ["undefined", "null", ""]:
        match_stage["$or"] = [
            {"warehouseId": warehouse_id},
            {"warehouse_id": warehouse_id}
        ]
    
    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {
            "$addFields": {
                "supplierIdStr": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "purchase_orders",
                "localField": "supplierIdStr",
                "foreignField": "supplierId",
                "as": "pos"
            }
        },
        {
            "$addFields": {
                "poCount": {"$size": "$pos"},
                "totalAmount": {
                    "$sum": "$pos.totalAmount"
                },
                "pendingAmount": {
                    "$sum": {
                        "$map": {
                            "input": "$pos",
                            "as": "po",
                            "in": {
                                "$cond": [
                                    {"$ne": ["$$po.status", "Received"]},
                                    {"$ifNull": ["$$po.totalAmount", 0]},
                                    0
                                ]
                            }
                        }
                    }
                },
                "paidAmount": {
                    "$sum": {
                        "$map": {
                            "input": "$pos",
                            "as": "po",
                            "in": {
                                "$cond": [
                                    {"$eq": ["$$po.status", "Received"]},
                                    {"$ifNull": ["$$po.totalAmount", 0]},
                                    0
                                ]
                            }
                        }
                    }
                },
                "productsSet": {
                    "$reduce": {
                        "input": "$pos",
                        "initialValue": [],
                        "in": {
                            "$setUnion": [
                                "$$value",
                                {
                                    "$filter": {
                                        "input": {
                                            "$map": {
                                                "input": {"$ifNull": ["$$this.items", []]},
                                                "as": "itm",
                                                "in": {"$ifNull": ["$$itm.productId", None]}
                                            }
                                        },
                                        "as": "pid",
                                        "cond": {"$ne": ["$$pid", None]}
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        },
        {
            "$addFields": {
                "products": {"$size": "$productsSet"}
            }
        },
        {
            "$project": {
                "pos": 0,
                "supplierIdStr": 0,
                "productsSet": 0
            }
        }
    ])
    
    cursor = db["suppliers"].aggregate(pipeline)
    suppliers = []
    async for s in cursor:
        s["id"] = str(s.pop("_id"))
        if "warehouse_id" in s and "warehouseId" not in s:
            s["warehouseId"] = s.pop("warehouse_id")
        suppliers.append(s)
    return suppliers

async def get_supplier(supplier_id: str, warehouse_id: Optional[str] = None) -> Optional[dict]:
    db = get_db()
    
    match_stage = {"_id": ObjectId(supplier_id)}
    if warehouse_id and warehouse_id not in ["undefined", "null", ""]:
        match_stage["$or"] = [
            {"warehouseId": warehouse_id},
            {"warehouse_id": warehouse_id}
        ]
        
    pipeline = [
        {"$match": match_stage},
        {
            "$addFields": {
                "supplierIdStr": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "purchase_orders",
                "localField": "supplierIdStr",
                "foreignField": "supplierId",
                "as": "pos"
            }
        },
        {
            "$addFields": {
                "poCount": {"$size": "$pos"},
                "totalAmount": {
                    "$sum": "$pos.totalAmount"
                },
                "pendingAmount": {
                    "$sum": {
                        "$map": {
                            "input": "$pos",
                            "as": "po",
                            "in": {
                                "$cond": [
                                    {"$ne": ["$$po.status", "Received"]},
                                    {"$ifNull": ["$$po.totalAmount", 0]},
                                    0
                                ]
                            }
                        }
                    }
                },
                "paidAmount": {
                    "$sum": {
                        "$map": {
                            "input": "$pos",
                            "as": "po",
                            "in": {
                                "$cond": [
                                    {"$eq": ["$$po.status", "Received"]},
                                    {"$ifNull": ["$$po.totalAmount", 0]},
                                    0
                                ]
                            }
                        }
                    }
                },
                "productsSet": {
                    "$reduce": {
                        "input": "$pos",
                        "initialValue": [],
                        "in": {
                            "$setUnion": [
                                "$$value",
                                {
                                    "$filter": {
                                        "input": {
                                            "$map": {
                                                "input": {"$ifNull": ["$$this.items", []]},
                                                "as": "itm",
                                                "in": {"$ifNull": ["$$itm.productId", None]}
                                            }
                                        },
                                        "as": "pid",
                                        "cond": {"$ne": ["$$pid", None]}
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        },
        {
            "$addFields": {
                "products": {"$size": "$productsSet"}
            }
        },
        {
            "$project": {
                "pos": 0,
                "supplierIdStr": 0,
                "productsSet": 0
            }
        }
    ]
    cursor = db["suppliers"].aggregate(pipeline)
    suppliers = []
    async for s in cursor:
        s["id"] = str(s.pop("_id"))
        if "warehouse_id" in s and "warehouseId" not in s:
            s["warehouseId"] = s.pop("warehouse_id")
        suppliers.append(s)
    return suppliers[0] if suppliers else None

async def create_supplier(supplier_in: SupplierCreate) -> dict:
    db = get_db()
    s_dict = supplier_in.model_dump()
    result = await db["suppliers"].insert_one(s_dict)
    return await get_supplier(str(result.inserted_id))

async def update_supplier(supplier_id: str, supplier_in: SupplierUpdate) -> Optional[dict]:
    db = get_db()
    update_data = supplier_in.model_dump(exclude_unset=True)
    if update_data:
        await db["suppliers"].update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": update_data}
        )
    return await get_supplier(supplier_id)

async def delete_supplier(supplier_id: str) -> bool:
    db = get_db()
    result = await db["suppliers"].delete_one({"_id": ObjectId(supplier_id)})
    return result.deleted_count > 0

# Purchase Orders
async def get_purchase_orders(warehouse_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    
    query = {}
    if warehouse_id and warehouse_id not in ["undefined", "null", ""]:
        query["$or"] = [
            {"warehouseId": warehouse_id},
            {"warehouse_id": warehouse_id}
        ]
        
    cursor = db["purchase_orders"].find(query)
    pos = []
    async for p in cursor:
        p["id"] = str(p.pop("_id"))
        pos.append(p)
    return pos

async def get_purchase_order(po_id: str) -> Optional[dict]:
    db = get_db()
    
    pipeline = [
        {"$match": {"_id": ObjectId(po_id)}},
        {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {"productObjectId": {
            "$cond": [{"$eq": ["$items.productId", ""]}, None, {"$toObjectId": "$items.productId"}]
        }}},
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
            "$addFields": {
                "items.unit": "$product_info.baseUnit"
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "poNumber": {"$first": "$poNumber"},
                "supplierId": {"$first": "$supplierId"},
                "supplierName": {"$first": "$supplierName"},
                "orderDate": {"$first": "$orderDate"},
                "expectedDelivery": {"$first": "$expectedDelivery"},
                "totalAmount": {"$first": "$totalAmount"},
                "status": {"$first": "$status"},
                "warehouseId": {"$first": "$warehouseId"},
                "items": {"$push": "$items"}
            }
        }
    ]
    
    cursor = db["purchase_orders"].aggregate(pipeline)
    pos = []
    async for p in cursor:
        p["id"] = str(p.pop("_id"))
        pos.append(p)
        
    return pos[0] if pos else None

async def create_purchase_order(po_in: PurchaseOrderCreate) -> dict:
    db = get_db()
    p_dict = po_in.model_dump()
    result = await db["purchase_orders"].insert_one(p_dict)
    return await get_purchase_order(str(result.inserted_id))

async def update_purchase_order(po_id: str, po_in: PurchaseOrderUpdate) -> Optional[dict]:
    db = get_db()
    
    # 1. Fetch previous purchase order status and warehouseId
    po = await db["purchase_orders"].find_one({"_id": ObjectId(po_id)})
    if not po:
        return None
    prev_status = po.get("status")
    warehouse_id = po.get("warehouseId")
    
    # 2. Update the purchase order in db
    update_data = po_in.model_dump(exclude_unset=True)
    if update_data:
        await db["purchase_orders"].update_one(
            {"_id": ObjectId(po_id)},
            {"$set": update_data}
        )
        
    # Get the updated PO to get full item list and new status
    updated_po = await db["purchase_orders"].find_one({"_id": ObjectId(po_id)})
    if not updated_po:
        return None
        
    new_status = updated_po.get("status")
    
    # 3. Check for transition to 'Completed' or 'Received'
    if new_status in ["Completed", "Received"] and prev_status not in ["Completed", "Received"]:
        items = updated_po.get("items", [])
        for item in items:
            product_id = item.get("productId")
            if not product_id:
                continue
                
            qty = item.get("receivedQuantity")
            if qty is None:
                qty = item.get("quantity", 0)
                
            if qty <= 0:
                continue
                
            # Find the warehouse product record
            wp = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
            
            if wp:
                prev_stock = wp.get("currentStock", 0)
                new_stock = prev_stock + qty
                actual_price = item.get("actualUnitPrice") or item.get("unitPrice") or 0.0
                
                await db["warehouse_products"].update_one(
                    {"_id": wp["_id"]},
                    {
                        "$inc": {
                            "currentStock": qty,
                            "availableStock": qty,
                            "stockIn": qty
                        },
                        "$set": {
                            "basePrice": actual_price
                        }
                    }
                )
            else:
                # If warehouse product record doesn't exist, create it!
                prev_stock = 0
                new_stock = qty
                
                # Fetch product info from products collection if available to copy imageUrl
                prod_details = await db["products"].find_one({"_id": ObjectId(product_id)})
                image_url = prod_details.get("imageUrl") if prod_details else None
                
                from app.schemas.warehouse_product import WarehouseProductCreate
                wp_create = WarehouseProductCreate(
                    productId=product_id,
                    warehouseId=warehouse_id,
                    initialStock=0,
                    currentStock=qty,
                    availableStock=qty,
                    stockIn=qty,
                    basePrice=item.get("actualUnitPrice") or item.get("unitPrice") or 0.0,
                    imageUrl=image_url
                )
                await db["warehouse_products"].insert_one(wp_create.model_dump())
                
            # Log the movement
            from app.schemas.inventory_movement import InventoryMovementCreate
            from app.crud.inventory_movement import log_movement
            from datetime import datetime
            
            movement = InventoryMovementCreate(
                productId=product_id,
                warehouseId=warehouse_id,
                type="Stock In",
                quantity=qty,
                prevStock=prev_stock,
                newStock=new_stock,
                reference=f"PO Received: {updated_po.get('poNumber')}",
                user="System",
                date=datetime.utcnow()
            )
            await log_movement(movement)
            
    return await get_purchase_order(po_id)

async def delete_purchase_order(po_id: str) -> bool:
    db = get_db()
    result = await db["purchase_orders"].delete_one({"_id": ObjectId(po_id)})
    return result.deleted_count > 0

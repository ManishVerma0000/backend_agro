from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.warehouse_product import WarehouseProductCreate, WarehouseProductUpdate, StockActionCreate

async def get_warehouse_products(warehouse_id: str = None) -> List[dict]:
    db = get_db()
    match_query = {}
    if warehouse_id:
        match_query["warehouseId"] = warehouse_id

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
            "$addFields": {
                "categoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.categoryId", ""]}, {"$ne": ["$product_info.categoryId", None]}]},
                        {"$toObjectId": "$product_info.categoryId"},
                        None
                    ]
                },
                "subcategoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.subcategoryId", ""]}, {"$ne": ["$product_info.subcategoryId", None]}]},
                        {"$toObjectId": "$product_info.subcategoryId"},
                        None
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "categoryObjectId",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "subcategories",
                "localField": "subcategoryObjectId",
                "foreignField": "_id",
                "as": "subcategory_info"
            }
        },
        {"$unwind": {"path": "$subcategory_info", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "productName": "$product_info.name",
                "category": "$category_info.name",
                "subcategory": "$subcategory_info.name",
                "hsnCode": "$product_info.hsn"
            }
        },
        {
            "$project": {
                "productObjectId": 0,
                "product_info": 0,
                "categoryObjectId": 0,
                "category_info": 0,
                "subcategoryObjectId": 0,
                "subcategory_info": 0
            }
        }
    ]
    
    cursor = db["warehouse_products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
    return products

async def get_warehouse_product(product_id: str) -> Optional[dict]:
    db = get_db()
    
    pipeline = [
        {"$match": {"_id": ObjectId(product_id)}},
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
            "$addFields": {
                "categoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.categoryId", ""]}, {"$ne": ["$product_info.categoryId", None]}]},
                        {"$toObjectId": "$product_info.categoryId"},
                        None
                    ]
                },
                "subcategoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.subcategoryId", ""]}, {"$ne": ["$product_info.subcategoryId", None]}]},
                        {"$toObjectId": "$product_info.subcategoryId"},
                        None
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "categoryObjectId",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "subcategories",
                "localField": "subcategoryObjectId",
                "foreignField": "_id",
                "as": "subcategory_info"
            }
        },
        {"$unwind": {"path": "$subcategory_info", "preserveNullAndEmptyArrays": True}},
        {
            "$addFields": {
                "productName": "$product_info.name",
                "category": "$category_info.name",
                "subcategory": "$subcategory_info.name",
                "hsnCode": "$product_info.hsn"
            }
        },
        {
            "$project": {
                "productObjectId": 0,
                "product_info": 0,
                "categoryObjectId": 0,
                "category_info": 0,
                "subcategoryObjectId": 0,
                "subcategory_info": 0
            }
        }
    ]
    
    cursor = db["warehouse_products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
        
    return products[0] if products else None

async def create_warehouse_product(product_in: WarehouseProductCreate) -> dict:
    db = get_db()
    prod_dict = product_in.model_dump()
    stock = prod_dict.get("initialStock", 0)
    prod_dict["currentStock"] = stock
    prod_dict["availableStock"] = stock
    prod_dict["stockIn"] = stock
    
    result = await db["warehouse_products"].insert_one(prod_dict)
    return await get_warehouse_product(str(result.inserted_id))

async def update_warehouse_product(product_id: str, product_in: WarehouseProductUpdate) -> Optional[dict]:
    db = get_db()
    update_data = product_in.model_dump(exclude_unset=True)
    if update_data:
        await db["warehouse_products"].update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
    return await get_warehouse_product(product_id)

async def delete_warehouse_product(product_id: str) -> bool:
    db = get_db()
    result = await db["warehouse_products"].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

async def apply_stock_action(product_id: str, action_in: StockActionCreate) -> Optional[dict]:
    db = get_db()
    prod = await db["warehouse_products"].find_one({"_id": ObjectId(product_id)})
    if not prod:
        return None

    qty = action_in.quantity
    action = action_in.actionType

    update_query = {"$inc": {}}

    if action == 'Add Stock':
        update_query["$inc"]["currentStock"] = qty
        update_query["$inc"]["availableStock"] = qty
        update_query["$inc"]["stockIn"] = qty
    elif action == 'Reduce Stock':
        update_query["$inc"]["currentStock"] = -qty
        update_query["$inc"]["availableStock"] = -qty
        update_query["$inc"]["stockOut"] = qty
    elif action == 'Update Missing Stock':
        update_query["$inc"]["currentStock"] = -qty
        update_query["$inc"]["availableStock"] = -qty
        update_query["$inc"]["missingStock"] = qty
    elif action == 'Update Wastage Stock':
        update_query["$inc"]["currentStock"] = -qty
        update_query["$inc"]["availableStock"] = -qty
        update_query["$inc"]["wastageStock"] = qty
    elif action == 'Update Reorder Level':
        # Reorder is $set, not $inc
        update_query = {"$set": {"reorderLevel": qty}}
    
    if update_query:
        await db["warehouse_products"].update_one(
            {"_id": ObjectId(product_id)},
            update_query
        )
    
    # Store action in a separate movements table in a real app, just updating stock for now
    
    return await get_warehouse_product(product_id)

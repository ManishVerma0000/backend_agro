from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.supplier_product import SupplierProductCreate, SupplierProductUpdate

async def get_supplier_products(supplier_id: str) -> List[dict]:
    db = get_db()
    pipeline = [
        {"$match": {"supplierId": supplier_id}},
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
                "unit": "$product_info.baseUnit"
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
    
    cursor = db["supplier_products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
    return products

async def get_all_supplier_products() -> List[dict]:
    db = get_db()
    cursor = db["supplier_products"].find({})
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
    return products

async def create_supplier_product(product_in: SupplierProductCreate) -> dict:
    db = get_db()
    prod_dict = product_in.model_dump()
    prod_dict["lastPrice"] = 0.0
    prod_dict["lastSupplied"] = None
    prod_dict["totalQtySupplied"] = 0
    
    result = await db["supplier_products"].insert_one(prod_dict)
    
    # Retrieve the inserted product with full details
    inserted_id = str(result.inserted_id)
    products = await get_supplier_products(prod_dict["supplierId"])
    # Find the one we just inserted
    for p in products:
        if p["id"] == inserted_id:
            return p
    return products[0] if products else None

async def update_supplier_product(product_id: str, product_in: SupplierProductUpdate) -> Optional[dict]:
    db = get_db()
    update_data = product_in.model_dump(exclude_unset=True)
    if update_data:
        await db["supplier_products"].update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
    # Re-fetch is slightly harder without supplierId, let's just find the doc first
    doc = await db["supplier_products"].find_one({"_id": ObjectId(product_id)})
    if doc:
        prods = await get_supplier_products(doc["supplierId"])
        for p in prods:
            if p["id"] == product_id:
                return p
    return None

async def delete_supplier_product(product_id: str) -> bool:
    db = get_db()
    result = await db["supplier_products"].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

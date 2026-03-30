from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate

async def get_products() -> List[dict]:
    db = get_db()
    
    pipeline = [
        {
            "$addFields": {
                "categoryObjectId": {"$toObjectId": "$categoryId"}
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
        {
            "$unwind": {
                "path": "$category_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "category": "$category_info.name"
            }
        },
        {
            "$project": {
                "categoryObjectId": 0,
                "category_info": 0
            }
        }
    ]
    
    cursor = db["products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
    return products

async def get_product(product_id: str) -> Optional[dict]:
    db = get_db()
    
    pipeline = [
        {
            "$match": {"_id": ObjectId(product_id)}
        },
        {
            "$addFields": {
                "categoryObjectId": {"$toObjectId": "$categoryId"}
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
        {
            "$unwind": {
                "path": "$category_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "category": "$category_info.name"
            }
        },
        {
            "$project": {
                "categoryObjectId": 0,
                "category_info": 0
            }
        }
    ]
    
    cursor = db["products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
        
    return products[0] if products else None

async def create_product(product_in: ProductCreate) -> dict:
    db = get_db()
    prod_dict = product_in.model_dump()
    result = await db["products"].insert_one(prod_dict)
    return await get_product(str(result.inserted_id))

async def update_product(product_id: str, product_in: ProductUpdate) -> Optional[dict]:
    db = get_db()
    update_data = product_in.model_dump(exclude_unset=True)
    if update_data:
        await db["products"].update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
    return await get_product(product_id)

async def delete_product(product_id: str) -> bool:
    db = get_db()
    result = await db["products"].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

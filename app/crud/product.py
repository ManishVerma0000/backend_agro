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

def calculate_b2b_rates(prod_dict: dict):
    base_price_str = prod_dict.get("basePrice", "0")
    base_margin_str = prod_dict.get("baseMargin", "0")
    slabs = prod_dict.get("b2bBulkSlabs", [])
    
    if slabs and base_price_str and base_margin_str:
        try:
            import re
            b_price = float(re.sub(r'[^0-9.]', '', str(base_price_str)))
            b_margin = float(re.sub(r'[^0-9.]', '', str(base_margin_str)))
            
            for i, slab in enumerate(slabs):
                eff_margin = b_margin - (i * 2)
                calc_rate = b_price * (1 + eff_margin / 100)
                slab["rate"] = f"₹{calc_rate:.2f}"
        except (ValueError, TypeError):
            pass
    return prod_dict

async def create_product(product_in: ProductCreate) -> dict:
    db = get_db()
    prod_dict = product_in.model_dump()
    prod_dict = calculate_b2b_rates(prod_dict)
    result = await db["products"].insert_one(prod_dict)
    return await get_product(str(result.inserted_id))

async def update_product(product_id: str, product_in: ProductUpdate) -> Optional[dict]:
    db = get_db()
    
    # Fetch existing to ensure we have all fields for rate calculation
    existing = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not existing:
        return None
        
    update_data = product_in.model_dump(exclude_unset=True)
    if update_data:
        # Merge existing with new updates for recalculation
        full_data = {**existing, **update_data}
        full_data = calculate_b2b_rates(full_data)
        
        # Only update the fields that were actually passed plus the recalculated slabs
        final_update = {**update_data}
        if "b2bBulkSlabs" in full_data:
            final_update["b2bBulkSlabs"] = full_data["b2bBulkSlabs"]
            
        await db["products"].update_one(
            {"_id": ObjectId(product_id)},
            {"$set": final_update}
        )
    return await get_product(product_id)

async def delete_product(product_id: str) -> bool:
    db = get_db()
    result = await db["products"].delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0

from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.warehouse_product import WarehouseProductCreate, WarehouseProductUpdate

async def get_warehouse_products(warehouse_id: str = None) -> List[dict]:
    db = get_db()
    query = {}
    if warehouse_id:
        query["warehouseId"] = warehouse_id
    cursor = db["warehouse_products"].find(query)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        products.append(prod)
    return products

async def get_warehouse_product(product_id: str) -> Optional[dict]:
    db = get_db()
    prod = await db["warehouse_products"].find_one({"_id": ObjectId(product_id)})
    if prod:
        prod["id"] = str(prod.pop("_id"))
    return prod

async def create_warehouse_product(product_in: WarehouseProductCreate) -> dict:
    db = get_db()
    prod_dict = product_in.model_dump()
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

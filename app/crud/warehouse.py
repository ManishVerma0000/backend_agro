from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate

async def get_warehouses() -> List[dict]:
    db = get_db()
    cursor = db["warehouses"].find()
    warehouses = []
    async for w in cursor:
        w["id"] = str(w.pop("_id"))
        warehouses.append(w)
    return warehouses

async def get_warehouse(warehouse_id: str) -> Optional[dict]:
    db = get_db()
    w = await db["warehouses"].find_one({"_id": ObjectId(warehouse_id)})
    if w:
        w["id"] = str(w.pop("_id"))
    return w

async def create_warehouse(warehouse_in: WarehouseCreate) -> dict:
    db = get_db()
    w_dict = warehouse_in.model_dump()
    result = await db["warehouses"].insert_one(w_dict)
    return await get_warehouse(str(result.inserted_id))

async def update_warehouse(warehouse_id: str, warehouse_in: WarehouseUpdate) -> Optional[dict]:
    db = get_db()
    update_data = warehouse_in.model_dump(exclude_unset=True)
    if update_data:
        await db["warehouses"].update_one(
            {"_id": ObjectId(warehouse_id)},
            {"$set": update_data}
        )
    return await get_warehouse(warehouse_id)

async def delete_warehouse(warehouse_id: str) -> bool:
    db = get_db()
    result = await db["warehouses"].delete_one({"_id": ObjectId(warehouse_id)})
    return result.deleted_count > 0

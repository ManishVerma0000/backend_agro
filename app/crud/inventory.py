from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.inventory import InventoryMovementCreate, InventoryMovementUpdate

async def get_movements() -> List[dict]:
    db = get_db()
    cursor = db["inventory_movements"].find()
    movements = []
    async for m in cursor:
        m["id"] = str(m.pop("_id"))
        movements.append(m)
    return movements

async def get_movement(movement_id: str) -> Optional[dict]:
    db = get_db()
    m = await db["inventory_movements"].find_one({"_id": ObjectId(movement_id)})
    if m:
        m["id"] = str(m.pop("_id"))
    return m

async def create_movement(movement_in: InventoryMovementCreate) -> dict:
    db = get_db()
    m_dict = movement_in.model_dump()
    result = await db["inventory_movements"].insert_one(m_dict)
    return await get_movement(str(result.inserted_id))

async def update_movement(movement_id: str, movement_in: InventoryMovementUpdate) -> Optional[dict]:
    db = get_db()
    update_data = movement_in.model_dump(exclude_unset=True)
    if update_data:
        await db["inventory_movements"].update_one(
            {"_id": ObjectId(movement_id)},
            {"$set": update_data}
        )
    return await get_movement(movement_id)

async def delete_movement(movement_id: str) -> bool:
    db = get_db()
    result = await db["inventory_movements"].delete_one({"_id": ObjectId(movement_id)})
    return result.deleted_count > 0

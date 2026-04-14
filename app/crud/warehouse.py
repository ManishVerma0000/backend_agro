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
    
    # Ensure overheadCost and logisticCost are explicitly set from the model attributes
    w_dict["overheadCost"] = float(warehouse_in.overheadCost)
    w_dict["logisticCost"] = float(warehouse_in.logisticCost)
    
    # Debug: Write to a file to verify what the backend receives
    with open("warehouse_debug.txt", "a") as f:
        f.write(f"CREATE DATA: {w_dict}\n")
    
    result = await db["warehouses"].insert_one(w_dict)
    return await get_warehouse(str(result.inserted_id))

async def update_warehouse(warehouse_id: str, warehouse_in: WarehouseUpdate) -> Optional[dict]:
    db = get_db()
    update_data = warehouse_in.model_dump(exclude_unset=True)
    if update_data:
        # Debug: Write to a file to verify what the backend receives
        with open("warehouse_debug.txt", "a") as f:
            f.write(f"UPDATE ID: {warehouse_id}, DATA: {update_data}\n")
            
        # Ensure proper type conversion if present
        if "overheadCost" in update_data and update_data["overheadCost"] is not None:
            update_data["overheadCost"] = float(update_data["overheadCost"])
        if "logisticCost" in update_data and update_data["logisticCost"] is not None:
            update_data["logisticCost"] = float(update_data["logisticCost"])
            
        await db["warehouses"].update_one(
            {"_id": ObjectId(warehouse_id)},
            {"$set": update_data}
        )
    return await get_warehouse(warehouse_id)

async def delete_warehouse(warehouse_id: str) -> bool:
    db = get_db()
    result = await db["warehouses"].delete_one({"_id": ObjectId(warehouse_id)})
    return result.deleted_count > 0

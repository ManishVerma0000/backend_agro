from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.inventory_movement import InventoryMovementCreate

async def log_movement(movement_in: InventoryMovementCreate) -> dict:
    db = get_db()
    movement_dict = movement_in.model_dump()
    result = await db["inventory_movements"].insert_one(movement_dict)
    
    new_movement = await db["inventory_movements"].find_one({"_id": result.inserted_id})
    new_movement["id"] = str(new_movement.pop("_id"))
    return new_movement

async def get_inventory_movements(warehouse_id: str = None) -> List[dict]:
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
                "productName": "$product_info.name",
                "unit": "$product_info.baseUnit"
            }
        },
        {
            "$project": {
                "productObjectId": 0,
                "product_info": 0
            }
        },
        {"$sort": {"date": -1}}
    ]

    cursor = db["inventory_movements"].aggregate(pipeline)
    movements = []
    async for mov in cursor:
        mov["id"] = str(mov.pop("_id"))
        movements.append(mov)
    return movements

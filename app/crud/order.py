from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderUpdate

async def get_orders() -> List[dict]:
    db = get_db()
    cursor = db["orders"].find()
    orders = []
    async for o in cursor:
        o["id"] = str(o.pop("_id"))
        orders.append(o)
    return orders

async def get_order(order_id: str) -> Optional[dict]:
    db = get_db()
    o = await db["orders"].find_one({"_id": ObjectId(order_id)})
    if o:
        o["id"] = str(o.pop("_id"))
    return o

async def create_order(order_in: OrderCreate) -> dict:
    db = get_db()
    o_dict = order_in.model_dump()
    result = await db["orders"].insert_one(o_dict)
    return await get_order(str(result.inserted_id))

async def update_order(order_id: str, order_in: OrderUpdate) -> Optional[dict]:
    db = get_db()
    update_data = order_in.model_dump(exclude_unset=True)
    if update_data:
        await db["orders"].update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
    return await get_order(order_id)

async def delete_order(order_id: str) -> bool:
    db = get_db()
    result = await db["orders"].delete_one({"_id": ObjectId(order_id)})
    return result.deleted_count > 0

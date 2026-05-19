from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.dispatch import DispatchCreate, DispatchUpdate
from datetime import datetime
from app.crud.mobile_order import update_order_status_in_db

async def generate_dispatch_id() -> str:
    db = get_db()
    year = datetime.now().year
    count = await db["dispatches"].count_documents({"dispatchId": {"$regex": f"^DIS-{year}-"}})
    return f"DIS-{year}-{str(count + 1).zfill(3)}"

async def create_dispatch(dispatch_in: DispatchCreate) -> dict:
    db = get_db()
    dispatch_dict = dispatch_in.model_dump()
    dispatch_dict["createdAt"] = datetime.utcnow()
    dispatch_dict["dispatchTime"] = datetime.utcnow()
    dispatch_dict["dispatchId"] = await generate_dispatch_id()
    
    result = await db["dispatches"].insert_one(dispatch_dict)
    
    # Update status of mobile orders to "Out for Delivery"
    for oid in dispatch_in.orderIds:
        await update_order_status_in_db(oid, "Out for Delivery", db)
        await db["mobile_orders"].update_one(
            {"_id": ObjectId(oid)},
            {"$set": {"dispatchId": str(result.inserted_id)}}
        )
    
    dispatch_dict["id"] = str(result.inserted_id)
    return dispatch_dict

async def get_all_dispatches(warehouse_id: str) -> List[dict]:
    db = get_db()
    cursor = db["dispatches"].find({"warehouseId": warehouse_id}).sort("createdAt", -1)
    dispatches = []
    async for dispatch in cursor:
        dispatch["id"] = str(dispatch.pop("_id"))
        dispatch["orderCount"] = len(dispatch.get("orderIds", []))
        dispatches.append(dispatch)
    return dispatches

async def get_dispatch(dispatch_id: str) -> Optional[dict]:
    db = get_db()
    dispatch = await db["dispatches"].find_one({"_id": ObjectId(dispatch_id)})
    if dispatch:
        dispatch["id"] = str(dispatch.pop("_id"))
        dispatch["orderCount"] = len(dispatch.get("orderIds", []))
    return dispatch

async def update_dispatch_status(dispatch_id: str, status: str) -> Optional[dict]:
    db = get_db()
    await db["dispatches"].update_one(
        {"_id": ObjectId(dispatch_id)},
        {"$set": {"status": status}}
    )
    # Update orders too
    dispatch = await get_dispatch(dispatch_id)
    if dispatch:
        for oid in dispatch["orderIds"]:
            await update_order_status_in_db(oid, status, db)
    return dispatch

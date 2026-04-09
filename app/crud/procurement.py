from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.procurement import SupplierCreate, SupplierUpdate, PurchaseOrderCreate, PurchaseOrderUpdate

# Suppliers
async def get_suppliers() -> List[dict]:
    db = get_db()
    cursor = db["suppliers"].find()
    suppliers = []
    async for s in cursor:
        s["id"] = str(s.pop("_id"))
        suppliers.append(s)
    return suppliers

async def get_supplier(supplier_id: str) -> Optional[dict]:
    db = get_db()
    s = await db["suppliers"].find_one({"_id": ObjectId(supplier_id)})
    if s:
        s["id"] = str(s.pop("_id"))
    return s

async def create_supplier(supplier_in: SupplierCreate) -> dict:
    db = get_db()
    s_dict = supplier_in.model_dump()
    result = await db["suppliers"].insert_one(s_dict)
    return await get_supplier(str(result.inserted_id))

async def update_supplier(supplier_id: str, supplier_in: SupplierUpdate) -> Optional[dict]:
    db = get_db()
    update_data = supplier_in.model_dump(exclude_unset=True)
    if update_data:
        await db["suppliers"].update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": update_data}
        )
    return await get_supplier(supplier_id)

async def delete_supplier(supplier_id: str) -> bool:
    db = get_db()
    result = await db["suppliers"].delete_one({"_id": ObjectId(supplier_id)})
    return result.deleted_count > 0

# Purchase Orders
async def get_purchase_orders() -> List[dict]:
    db = get_db()
    cursor = db["purchase_orders"].find()
    pos = []
    async for p in cursor:
        p["id"] = str(p.pop("_id"))
        pos.append(p)
    return pos

async def get_purchase_order(po_id: str) -> Optional[dict]:
    db = get_db()
    
    pipeline = [
        {"$match": {"_id": ObjectId(po_id)}},
        {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {"productObjectId": {
            "$cond": [{"$eq": ["$items.productId", ""]}, None, {"$toObjectId": "$items.productId"}]
        }}},
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
                "items.unit": "$product_info.baseUnit"
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "poNumber": {"$first": "$poNumber"},
                "supplierId": {"$first": "$supplierId"},
                "supplierName": {"$first": "$supplierName"},
                "orderDate": {"$first": "$orderDate"},
                "expectedDelivery": {"$first": "$expectedDelivery"},
                "totalAmount": {"$first": "$totalAmount"},
                "status": {"$first": "$status"},
                "items": {"$push": "$items"}
            }
        }
    ]
    
    cursor = db["purchase_orders"].aggregate(pipeline)
    pos = []
    async for p in cursor:
        p["id"] = str(p.pop("_id"))
        pos.append(p)
        
    return pos[0] if pos else None

async def create_purchase_order(po_in: PurchaseOrderCreate) -> dict:
    db = get_db()
    p_dict = po_in.model_dump()
    result = await db["purchase_orders"].insert_one(p_dict)
    return await get_purchase_order(str(result.inserted_id))

async def update_purchase_order(po_id: str, po_in: PurchaseOrderUpdate) -> Optional[dict]:
    db = get_db()
    update_data = po_in.model_dump(exclude_unset=True)
    if update_data:
        await db["purchase_orders"].update_one(
            {"_id": ObjectId(po_id)},
            {"$set": update_data}
        )
    return await get_purchase_order(po_id)

async def delete_purchase_order(po_id: str) -> bool:
    db = get_db()
    result = await db["purchase_orders"].delete_one({"_id": ObjectId(po_id)})
    return result.deleted_count > 0

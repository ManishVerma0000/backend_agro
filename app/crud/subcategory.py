from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate

async def get_subcategories() -> List[dict]:
    db = get_db()
    cursor = db["subcategories"].find()
    subcats = []
    async for subcat in cursor:
        subcat["id"] = str(subcat.pop("_id"))
        subcats.append(subcat)
    return subcats

async def get_subcategory(subcategory_id: str) -> Optional[dict]:
    db = get_db()
    subcat = await db["subcategories"].find_one({"_id": ObjectId(subcategory_id)})
    if subcat:
        subcat["id"] = str(subcat.pop("_id"))
    return subcat

async def create_subcategory(subcategory_in: SubcategoryCreate) -> dict:
    db = get_db()
    subcat_dict = subcategory_in.model_dump()
    result = await db["subcategories"].insert_one(subcat_dict)
    return await get_subcategory(str(result.inserted_id))

async def update_subcategory(subcategory_id: str, subcategory_in: SubcategoryUpdate) -> Optional[dict]:
    db = get_db()
    update_data = subcategory_in.model_dump(exclude_unset=True)
    if update_data:
        await db["subcategories"].update_one(
            {"_id": ObjectId(subcategory_id)},
            {"$set": update_data}
        )
    return await get_subcategory(subcategory_id)

async def delete_subcategory(subcategory_id: str) -> bool:
    db = get_db()
    result = await db["subcategories"].delete_one({"_id": ObjectId(subcategory_id)})
    return result.deleted_count > 0

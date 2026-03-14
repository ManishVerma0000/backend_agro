from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate

async def get_categories() -> List[dict]:
    db = get_db()
    cursor = db["categories"].find()
    categories = []
    async for cat in cursor:
        cat["id"] = str(cat.pop("_id"))
        categories.append(cat)
    return categories

async def get_category(category_id: str) -> Optional[dict]:
    db = get_db()
    cat = await db["categories"].find_one({"_id": ObjectId(category_id)})
    if cat:
        cat["id"] = str(cat.pop("_id"))
    return cat

async def create_category(category_in: CategoryCreate) -> dict:
    db = get_db()
    cat_dict = category_in.model_dump()
    result = await db["categories"].insert_one(cat_dict)
    return await get_category(str(result.inserted_id))

async def update_category(category_id: str, category_in: CategoryUpdate) -> Optional[dict]:
    db = get_db()
    update_data = category_in.model_dump(exclude_unset=True)
    if update_data:
        await db["categories"].update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_data}
        )
    return await get_category(category_id)

async def delete_category(category_id: str) -> bool:
    db = get_db()
    result = await db["categories"].delete_one({"_id": ObjectId(category_id)})
    return result.deleted_count > 0

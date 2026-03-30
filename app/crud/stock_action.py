from typing import List
from bson import ObjectId
from app.db.session import get_db
from app.schemas.stock_action import StockActionCreate

# Pre-defined defaults to seed into DB if empty
DEFAULT_ACTIONS = [
    {
        "label": "Add Stock",
        "iconName": "PlusIcon",
        "bg": "bg-[#10b981]",
        "text": "text-white",
        "hover": "hover:bg-[#059669]",
        "border": ""
    },
    {
        "label": "Reduce Stock",
        "iconName": "MinusIcon",
        "bg": "bg-[#fff7ed]",
        "text": "text-[#ea580c]",
        "hover": "hover:bg-[#ffedd5]",
        "border": "border border-[#ffedd5]"
    },
    {
        "label": "Update Missing Stock",
        "iconName": "AlertCircleIcon",
        "bg": "bg-[#fefce8]",
        "text": "text-[#b45309]",
        "hover": "hover:bg-[#fef9c3]",
        "border": "border border-[#fef9c3]"
    },
    {
        "label": "Update Wastage Stock",
        "iconName": "TrashIcon",
        "bg": "bg-[#fef2f2]",
        "text": "text-[#dc2626]",
        "hover": "hover:bg-[#fee2e2]",
        "border": "border border-[#fee2e2]"
    },
    {
        "label": "Update Reorder Level",
        "iconName": "SettingsIcon",
        "bg": "bg-[#faf5ff]",
        "text": "text-[#9333ea]",
        "hover": "hover:bg-[#f3e8ff]",
        "border": "border border-[#f3e8ff]"
    }
]

async def init_default_actions(db):
    """Seed the database with default actions if empty."""
    count = await db["stock_actions"].count_documents({})
    if count == 0:
        await db["stock_actions"].insert_many(DEFAULT_ACTIONS)

async def get_stock_actions() -> List[dict]:
    db = get_db()
    # Ensure initialized
    await init_default_actions(db)
    
    cursor = db["stock_actions"].find()
    actions = []
    async for action in cursor:
        action["id"] = str(action.pop("_id"))
        actions.append(action)
    return actions

async def create_stock_action(action_in: StockActionCreate) -> dict:
    db = get_db()
    action_dict = action_in.model_dump()
    result = await db["stock_actions"].insert_one(action_dict)
    
    new_action = await db["stock_actions"].find_one({"_id": result.inserted_id})
    new_action["id"] = str(new_action.pop("_id"))
    return new_action
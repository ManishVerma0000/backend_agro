from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.delivery_rule import DeliveryRuleCreate, DeliveryRuleUpdate
from datetime import datetime

async def create_delivery_rule(rule_in: DeliveryRuleCreate) -> dict:
    db = get_db()
    rule_dict = rule_in.model_dump()
    rule_dict["createdAt"] = datetime.utcnow()
    result = await db["delivery_rules"].insert_one(rule_dict)
    rule_dict["id"] = str(rule_dict.pop("_id"))
    return rule_dict

async def get_all_delivery_rules() -> List[dict]:
    db = get_db()
    cursor = db["delivery_rules"].find().sort("createdAt", -1)
    rules = []
    async for rule in cursor:
        rule["id"] = str(rule.pop("_id"))
        rules.append(rule)
    return rules

async def get_delivery_rule(rule_id: str) -> Optional[dict]:
    db = get_db()
    rule = await db["delivery_rules"].find_one({"_id": ObjectId(rule_id)})
    if rule:
        rule["id"] = str(rule.pop("_id"))
    return rule

async def update_delivery_rule(rule_id: str, rule_in: DeliveryRuleUpdate) -> Optional[dict]:
    db = get_db()
    update_data = rule_in.model_dump(exclude_unset=True)
    if update_data:
        await db["delivery_rules"].update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": update_data}
        )
    return await get_delivery_rule(rule_id)

async def delete_delivery_rule(rule_id: str) -> bool:
    db = get_db()
    result = await db["delivery_rules"].delete_one({"_id": ObjectId(rule_id)})
    return result.deleted_count > 0

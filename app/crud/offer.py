from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.offer import OfferCreate, OfferUpdate
from datetime import datetime

async def create_offer(offer_in: OfferCreate) -> dict:
    db = get_db()
    offer_dict = offer_in.model_dump()
    offer_dict["createdAt"] = datetime.utcnow()
    result = await db["offers"].insert_one(offer_dict)
    offer_dict["id"] = str(offer_dict.pop("_id"))
    return offer_dict

async def get_all_offers() -> List[dict]:
    db = get_db()
    cursor = db["offers"].find().sort("createdAt", -1)
    offers = []
    async for offer in cursor:
        offer["id"] = str(offer.pop("_id"))
        offers.append(offer)
    return offers

async def get_offer(offer_id: str) -> Optional[dict]:
    db = get_db()
    offer = await db["offers"].find_one({"_id": ObjectId(offer_id)})
    if offer:
        offer["id"] = str(offer.pop("_id"))
    return offer

async def update_offer(offer_id: str, offer_in: OfferUpdate) -> Optional[dict]:
    db = get_db()
    update_data = offer_in.model_dump(exclude_unset=True)
    if update_data:
        await db["offers"].update_one(
            {"_id": ObjectId(offer_id)},
            {"$set": update_data}
        )
    return await get_offer(offer_id)

async def delete_offer(offer_id: str) -> bool:
    db = get_db()
    result = await db["offers"].delete_one({"_id": ObjectId(offer_id)})
    return result.deleted_count > 0

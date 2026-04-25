from typing import Optional, List
from datetime import datetime
from app.db.session import get_db
from bson import ObjectId

async def get_applicable_offer(customer_id: str, cart_value: float) -> Optional[dict]:
    db = get_db()
    now = datetime.utcnow()
    
    # 1. Fetch customer details to check status (NEW / INACTIVE)
    customer = await db["customers"].find_one({"_id": ObjectId(customer_id)})
    if not customer:
        return None
        
    # Check order count
    order_count = await db["mobile_orders"].count_documents({"customerId": customer_id})
    is_new = order_count == 0
    
    # Check for INACTIVE (Win-back)
    # Let's say INACTIVE means no orders in last 30 days and has at least one order
    is_inactive = False
    if order_count > 0:
        last_order = await db["mobile_orders"].find_one(
            {"customerId": customer_id},
            sort=[("createdAt", -1)]
        )
        if last_order:
            days_since_last_order = (now - last_order["createdAt"]).days
            if days_since_last_order >= 30:
                is_inactive = True

    # 2. Fetch all Active offers
    cursor = db["offers"].find({
        "status": "Active",
        "validUntil": {"$gte": now}
    })
    
    all_offers = []
    async for offer in cursor:
        offer["id"] = str(offer.pop("_id"))
        all_offers.append(offer)
        
    # STEP 1: CHECK WIN-BACK
    if is_inactive:
        winback_offer = next((o for o in all_offers if o["offerType"] == "WIN-BACK"), None)
        if winback_offer:
            # Check usage
            usage = await db["offer_usage"].count_documents({"offerId": winback_offer["id"], "customerId": customer_id})
            if usage < winback_offer["usageLimit"]:
                return winback_offer
                
    # STEP 2: CHECK NEW CUSTOMER
    if is_new:
        new_offer = next((o for o in all_offers if o["offerType"] == "NEW CUSTOMER"), None)
        if new_offer:
            usage = await db["offer_usage"].count_documents({"offerId": new_offer["id"], "customerId": customer_id})
            if usage < new_offer["usageLimit"]:
                return new_offer
                
    # STEP 3: CHECK CART VALUE
    cart_offers = [o for o in all_offers if o["offerType"] == "CART VALUE" and cart_value >= o["minOrderValue"]]
    if cart_offers:
        # Sort by minOrderValue DESC to pick highest slab
        cart_offers.sort(key=lambda x: x["minOrderValue"], reverse=True)
        
        for offer in cart_offers:
            usage = await db["offer_usage"].count_documents({"offerId": offer["id"], "customerId": customer_id})
            if usage < offer["usageLimit"]:
                return offer
                
    return None

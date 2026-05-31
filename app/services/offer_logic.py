from typing import Optional, List
from datetime import datetime
from app.db.session import get_db
from bson import ObjectId
from app.crud.customer import get_customer_with_stats

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

async def evaluate_offer_rules(
    customer_id: Optional[str] = None,
    cart_value: float = 0.0,
    simulate_inactive: Optional[bool] = None,
    simulate_new: Optional[bool] = None
) -> dict:
    db = get_db()
    now = datetime.utcnow()
    logs = []
    
    # 1. Resolve Customer Segments
    is_inactive = False
    is_new = False
    customer_name = "Guest/Simulated"
    customer_phone = "N/A"
    resolved_status = "Active"
    resolved_type = "Low"
    total_orders = 0

    if customer_id:
        customer = await get_customer_with_stats(customer_id)
        if customer:
            customer_name = customer.get("shopName") or customer.get("ownerName") or "Unknown"
            customer_phone = customer.get("mobileNumber") or "N/A"
            total_orders = customer.get("totalOrders", 0)
            
            # Match status Inactive or At Risk
            resolved_status = customer.get("customerStatus", "Active")
            resolved_type = customer.get("customerType", "Low")
            
            # NEW is defined as 0 orders
            is_new = (resolved_type == "New" or total_orders == 0)
            # WIN-BACK is defined as Inactive status
            is_inactive = (resolved_status == "Inactive")
            
            logs.append(f"🔍 [Customer Resolution] Loaded database customer '{customer_name}' ({customer_phone}).")
            logs.append(f"   -> Orders: {total_orders} | Segment Status: '{resolved_status}' | Segment Type: '{resolved_type}'")
        else:
            logs.append(f"⚠️ [Customer Resolution] Customer with ID {customer_id} not found in database. Using defaults.")
    else:
        logs.append("ℹ️ [Customer Resolution] Running pure simulation without database customer.")

    # Apply manual simulation overrides if provided
    if simulate_inactive is not None:
        is_inactive = simulate_inactive
        resolved_status = "Inactive" if is_inactive else "Active"
        logs.append(f"⚙️ [Override] Manual override: Simulate Inactive (WIN-BACK) status = {is_inactive}")
    if simulate_new is not None:
        is_new = simulate_new
        resolved_type = "New" if is_new else "Low"
        if is_new:
            total_orders = 0
        logs.append(f"⚙️ [Override] Manual override: Simulate First-Time (NEW) customer = {is_new}")

    # 2. Fetch all Active and unexpired offers
    cursor = db["offers"].find({
        "status": "Active",
        "validUntil": {"$gte": now}
    })
    
    all_offers = []
    async for offer in cursor:
        offer["id"] = str(offer.pop("_id"))
        all_offers.append(offer)

    logs.append(f"📋 [Database Offers] Retrieved {len(all_offers)} active & unexpired offers from database.")

    # Helper function for usage verification
    async def get_usage_count(offer_id: str) -> int:
        if not customer_id:
            return 0
        return await db["offer_usage"].count_documents({"offerId": offer_id, "customerId": customer_id})

    # STEP 1: CHECK WIN-BACK
    logs.append("--- STEP 1: CHECK WIN-BACK OFFERS ---")
    if is_inactive:
        logs.append("✅ Condition met: Customer is INACTIVE.")
        winback_offers = [o for o in all_offers if o["offerType"] == "WIN-BACK"]
        if winback_offers:
            logs.append(f"-> Found {len(winback_offers)} WIN-BACK offer(s). Evaluating usage limit and dates...")
            for offer in winback_offers:
                usage_count = await get_usage_count(offer["id"])
                limit = offer["usageLimit"]
                logs.append(f"   -> Offer: '{offer['offerName']}' | Usage Limit: {limit} | Current Usage: {usage_count}")
                
                if usage_count < limit:
                    logs.append(f"🎉 SUCCESS: WIN-BACK offer '{offer['offerName']}' applied! Stopping evaluation.")
                    return {
                        "offer": offer,
                        "logs": logs,
                        "customerStatus": resolved_status,
                        "customerType": resolved_type,
                        "customerName": customer_name,
                        "customerPhone": customer_phone,
                        "totalOrders": total_orders
                    }
                else:
                    logs.append(f"   ❌ Rejected: Usage limit reached ({usage_count} >= {limit})")
        else:
            logs.append("⚠️ Rejected: No active WIN-BACK offers exist in the database.")
    else:
        logs.append("❌ Condition failed: Customer is not Inactive. WIN-BACK offers skipped.")

    # STEP 2: CHECK NEW CUSTOMER
    logs.append("--- STEP 2: CHECK NEW CUSTOMER OFFERS ---")
    if is_new:
        logs.append("✅ Condition met: Customer is NEW (first-time user).")
        new_offers = [o for o in all_offers if o["offerType"] == "NEW CUSTOMER"]
        if new_offers:
            logs.append(f"-> Found {len(new_offers)} NEW CUSTOMER offer(s). Evaluating usage limit and dates...")
            for offer in new_offers:
                usage_count = await get_usage_count(offer["id"])
                limit = offer["usageLimit"]
                logs.append(f"   -> Offer: '{offer['offerName']}' | Usage Limit: {limit} | Current Usage: {usage_count}")
                
                if usage_count < limit:
                    logs.append(f"🎉 SUCCESS: NEW CUSTOMER offer '{offer['offerName']}' applied! Stopping evaluation.")
                    return {
                        "offer": offer,
                        "logs": logs,
                        "customerStatus": resolved_status,
                        "customerType": resolved_type,
                        "customerName": customer_name,
                        "customerPhone": customer_phone,
                        "totalOrders": total_orders
                    }
                else:
                    logs.append(f"   ❌ Rejected: Usage limit reached ({usage_count} >= {limit})")
        else:
            logs.append("⚠️ Rejected: No active NEW CUSTOMER offers exist in the database.")
    else:
        logs.append("❌ Condition failed: Customer is not a first-time user. NEW CUSTOMER offers skipped.")

    # STEP 3: CHECK CART VALUE OFFERS
    logs.append("--- STEP 3: CHECK CART VALUE OFFERS ---")
    cart_offers = [o for o in all_offers if o["offerType"] == "CART VALUE"]
    if cart_offers:
        # Sort by minOrderValue descending to prioritize higher slab
        cart_offers.sort(key=lambda x: x["minOrderValue"], reverse=True)
        logs.append(f"-> Found {len(cart_offers)} active CART VALUE offer(s). Sorting descending by minimum order value to evaluate best slab...")
        
        for offer in cart_offers:
            min_val = offer["minOrderValue"]
            logs.append(f"   -> Offer: '{offer['offerName']}' | Minimum Order Value required: {min_val} | Current Cart Value: {cart_value}")
            
            if cart_value >= min_val:
                logs.append("      ✅ Cart value is sufficient.")
                usage_count = await get_usage_count(offer["id"])
                limit = offer["usageLimit"]
                logs.append(f"      -> Usage Limit: {limit} | Current Usage: {usage_count}")
                
                if usage_count < limit:
                    logs.append(f"🎉 SUCCESS: CART VALUE offer '{offer['offerName']}' applied!")
                    return {
                        "offer": offer,
                        "logs": logs,
                        "customerStatus": resolved_status,
                        "customerType": resolved_type,
                        "customerName": customer_name,
                        "customerPhone": customer_phone,
                        "totalOrders": total_orders
                    }
                else:
                    logs.append(f"      ❌ Rejected: Usage limit reached ({usage_count} >= {limit})")
            else:
                logs.append("      ❌ Rejected: Cart value is below minimum required.")
    else:
        logs.append("⚠️ Rejected: No active CART VALUE offers exist in the database.")

    # STEP 4: FALLBACK / NO OFFER
    logs.append("--- FINAL RESULT ---")
    logs.append("❌ No applicable offer could be resolved for this configuration.")
    return {
        "offer": None,
        "logs": logs,
        "customerStatus": resolved_status,
        "customerType": resolved_type,
        "customerName": customer_name,
        "customerPhone": customer_phone,
        "totalOrders": total_orders
    }


from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse
from app.crud.offer import (
    create_offer,
    get_all_offers,
    get_offer,
    update_offer,
    delete_offer
)

router = APIRouter()

@router.post("/", response_model=OfferResponse)
async def create_new_offer(offer: OfferCreate):
    return await create_offer(offer)

@router.get("/", response_model=List[OfferResponse])
async def read_offers():
    return await get_all_offers()

@router.get("/{id}", response_model=OfferResponse)
async def read_offer(id: str):
    offer = await get_offer(id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@router.put("/{id}", response_model=OfferResponse)
async def update_existing_offer(id: str, offer: OfferUpdate):
    updated_offer = await update_offer(id, offer)
    if not updated_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return updated_offer

@router.delete("/{id}")
async def remove_offer(id: str):
    success = await delete_offer(id)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found")
    return {"message": "Offer deleted successfully"}

from pydantic import BaseModel
from app.services.offer_logic import evaluate_offer_rules

class OfferEvaluationRequest(BaseModel):
    customerId: Optional[str] = None
    cartValue: float = 0.0
    simulateInactive: Optional[bool] = None
    simulateNew: Optional[bool] = None

@router.post("/evaluate")
async def evaluate_offer(payload: OfferEvaluationRequest):
    try:
        return await evaluate_offer_rules(
            customer_id=payload.customerId,
            cart_value=payload.cartValue,
            simulate_inactive=payload.simulateInactive,
            simulate_new=payload.simulateNew
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/valid")
async def get_valid_offers(
    customer_id: Optional[str] = None,
    cart_value: float = 0.0
):
    """
    Get all active and unexpired offers, with a dynamically computed 'isValid' flag
    evaluated on conditional basis based on customer status, type, order history,
    and current checkout cart value.
    """
    from app.db.session import get_db
    from app.crud.customer import get_customer_with_stats
    from datetime import datetime

    db = get_db()
    now = datetime.utcnow()

    # 1. Fetch active and unexpired offers
    cursor = db["offers"].find({
        "status": "Active",
        "validUntil": {"$gte": now}
    })
    
    offers = []
    async for offer in cursor:
        offer["id"] = str(offer.pop("_id"))
        offers.append(offer)

    # 2. Determine eligibility parameters if customer_id is provided
    is_inactive = False
    is_new = False
    customer_exists = False

    if customer_id:
        try:
            customer = await get_customer_with_stats(customer_id)
            if customer:
                customer_exists = True
                resolved_status = customer.get("customerStatus", "Active")
                resolved_type = customer.get("customerType", "Low")
                total_orders = customer.get("totalOrders", 0)

                is_new = (resolved_type == "New" or total_orders == 0)
                is_inactive = (resolved_status == "Inactive")
        except Exception as e:
            # Log error and proceed with defaults
            print(f"Error resolving customer stats for offer validity: {e}")

    # Helper function for usage verification
    async def get_usage_count(offer_id: str) -> int:
        if not customer_id:
            return 0
        return await db["offer_usage"].count_documents({"offerId": offer_id, "customerId": customer_id})

    # 3. Compute isValid dynamically for each offer
    for offer in offers:
        offer_id = offer["id"]
        offer_type = offer["offerType"]
        min_order = offer["minOrderValue"]
        usage_limit = offer["usageLimit"]

        is_valid = True

        # Check usage limit
        if customer_id:
            usage_count = await get_usage_count(offer_id)
            if usage_count >= usage_limit:
                is_valid = False

        # Check conditions based on type
        if is_valid:
            if offer_type == "WIN-BACK":
                # Only valid if the customer is Inactive
                if not customer_id or not customer_exists or not is_inactive:
                    is_valid = False
            elif offer_type == "NEW CUSTOMER":
                # Only valid if the customer is New
                if not customer_id or not customer_exists or not is_new:
                    is_valid = False
            elif offer_type == "CART VALUE":
                # Valid if cart_value >= min_order
                if cart_value < min_order:
                    is_valid = False

        offer["isValid"] = is_valid

    return offers



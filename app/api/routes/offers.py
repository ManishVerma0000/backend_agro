from fastapi import APIRouter, HTTPException
from typing import List
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

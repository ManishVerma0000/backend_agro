from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.delivery_rule import DeliveryRuleCreate, DeliveryRuleUpdate, DeliveryRuleResponse
from app.crud.delivery_rule import (
    create_delivery_rule,
    get_all_delivery_rules,
    get_delivery_rule,
    update_delivery_rule,
    delete_delivery_rule
)

router = APIRouter()

@router.post("/", response_model=DeliveryRuleResponse)
async def create_rule(rule: DeliveryRuleCreate):
    return await create_delivery_rule(rule)

@router.get("/", response_model=List[DeliveryRuleResponse])
async def get_rules():
    return await get_all_delivery_rules()

@router.get("/{id}", response_model=DeliveryRuleResponse)
async def get_rule(id: str):
    rule = await get_delivery_rule(id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{id}", response_model=DeliveryRuleResponse)
async def update_rule(id: str, rule: DeliveryRuleUpdate):
    updated_rule = await update_delivery_rule(id, rule)
    if not updated_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated_rule

@router.delete("/{id}")
async def delete_rule(id: str):
    success = await delete_delivery_rule(id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}

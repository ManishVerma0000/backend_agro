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
    if rule.isFreeDelivery:
        existing_rules = await get_all_delivery_rules()
        if any(r.get("isFreeDelivery") for r in existing_rules):
            raise HTTPException(status_code=400, detail="A free delivery rule already exists.")
    return await create_delivery_rule(rule)

@router.get("/", response_model=List[DeliveryRuleResponse])
async def get_rules():
    return await get_all_delivery_rules()

@router.get("/free-delivery", response_model=DeliveryRuleResponse)
async def get_free_delivery_rule():
    existing_rules = await get_all_delivery_rules()
    for rule in existing_rules:
        if rule.get("isFreeDelivery"):
            return rule
    raise HTTPException(status_code=404, detail="No free delivery rule found.")

@router.get("/warehouse/{warehouse_id}", response_model=List[DeliveryRuleResponse])
async def get_rules_by_warehouse(warehouse_id: str):
    all_rules = await get_all_delivery_rules()
    return [r for r in all_rules if r.get("warehouseId") == warehouse_id]

@router.get("/{id}", response_model=DeliveryRuleResponse)
async def get_rule(id: str):
    rule = await get_delivery_rule(id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{id}", response_model=DeliveryRuleResponse)
async def update_rule(id: str, rule: DeliveryRuleUpdate):
    if rule.isFreeDelivery:
        existing_rules = await get_all_delivery_rules()
        if any(r.get("isFreeDelivery") and r.get("id") != id for r in existing_rules):
            raise HTTPException(status_code=400, detail="A free delivery rule already exists.")
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

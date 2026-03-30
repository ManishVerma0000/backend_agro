from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.stock_action import StockActionResponse, StockActionCreate
from app.crud.stock_action import get_stock_actions, create_stock_action

router = APIRouter()

@router.get("/", response_model=List[StockActionResponse])
async def read_stock_actions():
    return await get_stock_actions()

@router.post("/", response_model=StockActionResponse)
async def create_stock_action_endpoint(action_in: StockActionCreate):
    return await create_stock_action(action_in)
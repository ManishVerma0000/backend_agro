from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.dispatch import DispatchCreate, DispatchUpdate, DispatchResponse
from app.crud.dispatch import (
    create_dispatch,
    get_all_dispatches,
    get_dispatch,
    update_dispatch_status
)

router = APIRouter()

@router.post("/", response_model=DispatchResponse)
async def create_new_dispatch(dispatch: DispatchCreate):
    return await create_dispatch(dispatch)

@router.get("/", response_model=List[DispatchResponse])
async def read_dispatches(warehouse_id: str = Query(...)):
    return await get_all_dispatches(warehouse_id)

@router.get("/{id}", response_model=DispatchResponse)
async def read_dispatch(id: str):
    dispatch = await get_dispatch(id)
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return dispatch

@router.patch("/{id}/status")
async def update_status(id: str, status: str):
    updated = await update_dispatch_status(id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return updated

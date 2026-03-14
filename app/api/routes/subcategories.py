from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate, SubcategoryResponse
from app.crud import subcategory as crud_subcategory

router = APIRouter()

@router.get("/", response_model=List[SubcategoryResponse])
async def read_subcategories():
    subcategories = await crud_subcategory.get_subcategories()
    return subcategories

@router.post("/", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory(subcategory_in: SubcategoryCreate):
    subcategory = await crud_subcategory.create_subcategory(subcategory_in)
    return subcategory

@router.get("/{subcategory_id}", response_model=SubcategoryResponse)
async def read_subcategory(subcategory_id: str):
    subcategory = await crud_subcategory.get_subcategory(subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory

@router.put("/{subcategory_id}", response_model=SubcategoryResponse)
async def update_subcategory(subcategory_id: str, subcategory_in: SubcategoryUpdate):
    subcategory = await crud_subcategory.update_subcategory(subcategory_id, subcategory_in)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory

@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory(subcategory_id: str):
    success = await crud_subcategory.delete_subcategory(subcategory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subcategory not found")

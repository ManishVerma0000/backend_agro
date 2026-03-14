from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as crud_category

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def read_categories():
    categories = await crud_category.get_categories()
    return categories

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate):
    category = await crud_category.create_category(category_in)
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(category_id: str):
    category = await crud_category.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category_in: CategoryUpdate):
    category = await crud_category.update_category(category_id, category_in)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str):
    success = await crud_category.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")

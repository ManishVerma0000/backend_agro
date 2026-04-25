from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from fastapi import APIRouter, HTTPException, status, Query
from app.crud import product as crud_product

router = APIRouter()

@router.get("/", response_model=ProductListResponse)
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return await crud_product.get_products(skip, limit)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate):
    product = await crud_product.create_product(product_in)
    return product

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: str):
    product = await crud_product.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_in: ProductUpdate):
    product = await crud_product.update_product(product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    success = await crud_product.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.procurement import SupplierCreate, SupplierUpdate, SupplierResponse, PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse
from app.schemas.supplier_product import SupplierProductCreate, SupplierProductUpdate, SupplierProductResponse
from app.crud import procurement as crud_procurement
from app.crud import supplier_product as crud_supplier_product

router = APIRouter()

# Suppliers
@router.get("/suppliers", response_model=List[SupplierResponse])
async def read_suppliers():
    return await crud_procurement.get_suppliers()

@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(supplier_in: SupplierCreate):
    return await crud_procurement.create_supplier(supplier_in)

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def read_supplier(supplier_id: str):
    s = await crud_procurement.get_supplier(supplier_id)
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return s

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: str, supplier_in: SupplierUpdate):
    s = await crud_procurement.update_supplier(supplier_id, supplier_in)
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return s

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: str):
    success = await crud_procurement.delete_supplier(supplier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Supplier not found")

# Supplier Products
@router.get("/suppliers/{supplier_id}/products", response_model=List[SupplierProductResponse])
async def read_supplier_products(supplier_id: str):
    return await crud_supplier_product.get_supplier_products(supplier_id)

@router.get("/supplier-products", response_model=List[SupplierProductResponse])
async def read_all_supplier_products():
    return await crud_supplier_product.get_all_supplier_products()

@router.post("/supplier-products", response_model=SupplierProductResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_product(product_in: SupplierProductCreate):
    return await crud_supplier_product.create_supplier_product(product_in)

@router.put("/supplier-products/{product_id}", response_model=SupplierProductResponse)
async def update_supplier_product(product_id: str, product_in: SupplierProductUpdate):
    p = await crud_supplier_product.update_supplier_product(product_id, product_in)
    if not p:
        raise HTTPException(status_code=404, detail="Supplier Product not found")
    return p

@router.delete("/supplier-products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier_product(product_id: str):
    success = await crud_supplier_product.delete_supplier_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Supplier Product not found")

# Purchase Orders
@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def read_purchase_orders():
    return await crud_procurement.get_purchase_orders()

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(po_in: PurchaseOrderCreate):
    return await crud_procurement.create_purchase_order(po_in)

@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
async def read_purchase_order(po_id: str):
    p = await crud_procurement.get_purchase_order(po_id)
    if not p:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return p

@router.put("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(po_id: str, po_in: PurchaseOrderUpdate):
    p = await crud_procurement.update_purchase_order(po_id, po_in)
    if not p:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return p

@router.delete("/purchase-orders/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(po_id: str):
    success = await crud_procurement.delete_purchase_order(po_id)
    if not success:
        raise HTTPException(status_code=404, detail="Purchase Order not found")

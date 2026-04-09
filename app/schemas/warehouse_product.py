from pydantic import BaseModel, ConfigDict
from typing import Optional

class WarehouseProductBase(BaseModel):
    productId: str
    warehouseId: Optional[str] = None
    initialStock: Optional[int] = 0
    currentStock: Optional[int] = 0
    availableStock: Optional[int] = 0
    reservedStock: Optional[int] = 0
    stockIn: Optional[int] = 0
    stockOut: Optional[int] = 0
    missingStock: Optional[int] = 0
    wastageStock: Optional[int] = 0
    reorderLevel: Optional[int] = 0
    basePrice: Optional[float] = 0.0
    location: Optional[str] = None
    status: Optional[str] = "Active"

class WarehouseProductCreate(WarehouseProductBase):
    pass

class WarehouseProductUpdate(BaseModel):
    initialStock: Optional[int] = None
    currentStock: Optional[int] = None
    availableStock: Optional[int] = None
    reservedStock: Optional[int] = None
    stockIn: Optional[int] = None
    stockOut: Optional[int] = None
    missingStock: Optional[int] = None
    wastageStock: Optional[int] = None
    reorderLevel: Optional[int] = None
    basePrice: Optional[float] = None
    location: Optional[str] = None
    status: Optional[str] = None

class WarehouseProductResponse(WarehouseProductBase):
    id: str
    productName: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    hsnCode: Optional[str] = None
    sellingPrice: Optional[float] = 0.0
    
    model_config = ConfigDict(populate_by_name=True)

class StockActionCreate(BaseModel):
    actionType: str
    quantity: int
    reason: Optional[str] = None
    notes: Optional[str] = None

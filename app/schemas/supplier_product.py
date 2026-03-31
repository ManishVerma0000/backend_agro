from pydantic import BaseModel, ConfigDict
from typing import Optional

class SupplierProductBase(BaseModel):
    supplierId: str
    productId: str
    basePrice: Optional[float] = 0.0
    status: Optional[str] = "Active"

class SupplierProductCreate(SupplierProductBase):
    pass

class SupplierProductUpdate(BaseModel):
    basePrice: Optional[float] = None
    status: Optional[str] = None

class SupplierProductResponse(SupplierProductBase):
    id: str
    productName: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    unit: Optional[str] = None
    lastPrice: Optional[float] = 0.0
    lastSupplied: Optional[str] = None
    totalQtySupplied: Optional[int] = 0
    
    model_config = ConfigDict(populate_by_name=True)

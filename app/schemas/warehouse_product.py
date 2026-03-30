from pydantic import BaseModel, ConfigDict
from typing import Optional

class WarehouseProductBase(BaseModel):
    productId: str
    warehouseId: Optional[str] = None
    initialStock: Optional[int] = 0
    reorderLevel: Optional[int] = 0
    basePrice: Optional[float] = 0.0
    location: Optional[str] = None
    status: Optional[str] = "Active"

class WarehouseProductCreate(WarehouseProductBase):
    pass

class WarehouseProductUpdate(BaseModel):
    initialStock: Optional[int] = None
    reorderLevel: Optional[int] = None
    basePrice: Optional[float] = None
    location: Optional[str] = None
    status: Optional[str] = None

class WarehouseProductResponse(WarehouseProductBase):
    id: str
    
    model_config = ConfigDict(populate_by_name=True)

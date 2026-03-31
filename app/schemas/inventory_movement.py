from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InventoryMovementBase(BaseModel):
    productId: str
    warehouseId: Optional[str] = None
    type: str # 'Stock In', 'Order Fulfillment', 'Stock Adjustment', 'Wastage', 'Missing Stock'
    quantity: int # Positive for addition, negative for reduction
    prevStock: int
    newStock: int
    reference: Optional[str] = None
    user: Optional[str] = None
    date: datetime

class InventoryMovementCreate(InventoryMovementBase):
    pass

class InventoryMovementResponse(InventoryMovementBase):
    id: str
    productName: Optional[str] = None
    unit: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)

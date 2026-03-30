from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class InventoryMovementBase(BaseModel):
    productId: str
    productName: str
    type: str # 'IN', 'OUT', 'WASTAGE', 'MISSING', 'RESERVED'
    quantity: int
    date: str
    reference: Optional[str] = None # e.g., PO Number or Order ID
    remarks: Optional[str] = None

class InventoryMovementCreate(InventoryMovementBase):
    pass

class InventoryMovementUpdate(BaseModel):
    type: Optional[str] = None
    quantity: Optional[int] = None
    date: Optional[str] = None
    reference: Optional[str] = None
    remarks: Optional[str] = None

class InventoryMovementResponse(InventoryMovementBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

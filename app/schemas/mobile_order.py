from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class MobileOrderCreate(BaseModel):
    customerId: str
    warehouseId: str
    deliveryAddressId: Optional[str] = None
    paymentMethod: Optional[str] = "Cash on Delivery"
    # Admin Panel Fields (If provided, we skip cart fetching)
    items: Optional[List[Any]] = None
    subtotal: Optional[float] = None
    deliveryFee: Optional[float] = None
    grandTotal: Optional[float] = None

class MobileOrderResponse(BaseModel):
    id: str
    customerId: str
    warehouseId: str
    deliveryAddressId: Optional[str] = None
    subtotal: float
    deliveryFee: float
    grandTotal: float
    paymentMethod: str
    status: str
    createdAt: datetime
    items: List[Any] = []
    
    model_config = ConfigDict(populate_by_name=True)

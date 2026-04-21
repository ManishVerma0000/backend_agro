from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class MobileOrderCreate(BaseModel):
    customerId: Optional[str] = None
    warehouseId: Optional[str] = None
    deliveryAddressId: Optional[str] = None
    address: Optional[Any] = None
    paymentMethod: Optional[str] = "Cash on Delivery"
    
    # Items
    items: Optional[List[Any]] = None
    cartItems: Optional[List[Any]] = None
    
    subtotal: Optional[float] = None
    deliveryFee: Optional[float] = None
    grandTotal: Optional[float] = None
    selectedDeliveryTime: Optional[str] = None

class MobileOrderResponse(BaseModel):
    id: str
    customerId: Optional[str] = None
    warehouseId: Optional[str] = None
    deliveryAddressId: Optional[str] = None
    subtotal: float
    deliveryFee: float
    grandTotal: float
    paymentMethod: str
    status: str
    createdAt: datetime
    items: List[Any] = []
    
    model_config = ConfigDict(populate_by_name=True)

class MobileOrderListResponse(BaseModel):
    items: List[MobileOrderResponse]
    total: int
    skip: int
    limit: int

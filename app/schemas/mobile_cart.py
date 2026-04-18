from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any

class MobileCartItemBase(BaseModel):
    customerId: str
    warehouseId: str
    productId: str
    quantity: int
    is_item_added_cart: Optional[bool] = None
    is_order_place: Optional[bool] = False
    is_item_removed: Optional[bool] = False

class MobileCartItemCreate(BaseModel):
    customerId: str
    warehouseId: str
    productId: str
    quantity: int

class MobileCartItemUpdate(BaseModel):
    quantity: int

class MobileCartBulkUpdate(BaseModel):
    customerId: str
    warehouseId: str
    items: List[dict] # List of {productId: str, quantity: int}

class MobileCartItemResponse(MobileCartItemBase):
    id: str
    productDetails: Optional[Any] = None
    
    model_config = ConfigDict(populate_by_name=True)

class MobileCartResponse(BaseModel):
    items: List[MobileCartItemResponse]
    subtotal: float
    deliveryFee: float
    grandTotal: float

from pydantic import BaseModel, ConfigDict
from typing import Optional

class OrderBase(BaseModel):
    orderId: str
    date: str
    customerName: str
    totalAmount: str
    status: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    orderId: Optional[str] = None
    date: Optional[str] = None
    customerName: Optional[str] = None
    totalAmount: Optional[str] = None
    status: Optional[str] = None

class OrderResponse(OrderBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

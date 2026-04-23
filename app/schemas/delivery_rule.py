from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeliveryRuleBase(BaseModel):
    ruleName: str
    minOrderValue: float
    maxOrderValue: Optional[float] = None
    deliveryCharge: float
    isFreeDelivery: bool = False
    status: str = "Active"

class DeliveryRuleCreate(DeliveryRuleBase):
    pass

class DeliveryRuleUpdate(BaseModel):
    ruleName: Optional[str] = None
    minOrderValue: Optional[float] = None
    maxOrderValue: Optional[float] = None
    deliveryCharge: Optional[float] = None
    isFreeDelivery: Optional[bool] = None
    status: Optional[str] = None

class DeliveryRuleResponse(DeliveryRuleBase):
    id: str
    createdAt: datetime

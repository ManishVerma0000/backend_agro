from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeliveryRuleBase(BaseModel):
    ruleName: Optional[str] = None
    minOrderValue: Optional[float] = None
    deliveryCharge: Optional[float] = None
    isFreeDelivery: bool = False
    bannerUrl: Optional[str] = None
    warehouseId: Optional[str] = None
    status: str = "Active"

class DeliveryRuleCreate(DeliveryRuleBase):
    pass

class DeliveryRuleUpdate(BaseModel):
    ruleName: Optional[str] = None
    minOrderValue: Optional[float] = None
    deliveryCharge: Optional[float] = None
    isFreeDelivery: Optional[bool] = None
    bannerUrl: Optional[str] = None
    warehouseId: Optional[str] = None
    status: Optional[str] = None

class DeliveryRuleResponse(DeliveryRuleBase):
    id: str
    createdAt: datetime

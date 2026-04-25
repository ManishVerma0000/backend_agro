from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class OfferBase(BaseModel):
    offerName: str
    offerType: Literal["CART VALUE", "NEW CUSTOMER", "WIN-BACK"]
    minOrderValue: float
    benefitType: Literal["L", "M", "H", "Flat"]
    benefitValue: float
    usageLimit: int
    usageType: Literal["Monthly", "Weekly", "Once", "Unlimited"]
    validUntil: datetime
    status: Literal["Active", "Inactive"] = "Active"
    imageUrl: Optional[str] = None

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    offerName: Optional[str] = None
    offerType: Optional[Literal["CART VALUE", "NEW CUSTOMER", "WIN-BACK"]] = None
    minOrderValue: Optional[float] = None
    benefitType: Optional[Literal["L", "M", "H", "Flat"]] = None
    benefitValue: Optional[float] = None
    usageLimit: Optional[int] = None
    usageType: Optional[Literal["Monthly", "Weekly", "Once", "Unlimited"]] = None
    validUntil: Optional[datetime] = None
    status: Optional[Literal["Active", "Inactive"]] = None
    imageUrl: Optional[str] = None

class OfferResponse(OfferBase):
    id: str
    createdAt: datetime

from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class DispatchBase(BaseModel):
    vehicleNumber: str
    driverName: str
    orderIds: List[str]
    route: str
    status: Literal["Out for Delivery", "Delivered", "Pending"] = "Pending"
    warehouseId: str

class DispatchCreate(DispatchBase):
    pass

class DispatchUpdate(BaseModel):
    status: Optional[Literal["Out for Delivery", "Delivered", "Pending"]] = None
    vehicleNumber: Optional[str] = None
    driverName: Optional[str] = None
    route: Optional[str] = None

class DispatchResponse(DispatchBase):
    id: str
    dispatchId: str
    createdAt: datetime
    dispatchTime: Optional[datetime] = None

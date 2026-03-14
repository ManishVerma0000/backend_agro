from pydantic import BaseModel, ConfigDict
from typing import Optional

class WarehouseBase(BaseModel):
    name: str
    manager: str
    contact: str
    location: str
    email: str
    state: str
    city: str
    pinCode: str
    gstNo: str = ""
    fssaiNo: str = ""
    openTime: str = ""
    closeTime: str = ""
    gstOwner: str = ""
    latitudeLink: str = ""
    images: list[str] = []
    documents: list[str] = []
    status: str
    createdDate: str

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    manager: Optional[str] = None
    contact: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pinCode: Optional[str] = None
    gstNo: Optional[str] = None
    fssaiNo: Optional[str] = None
    openTime: Optional[str] = None
    closeTime: Optional[str] = None
    gstOwner: Optional[str] = None
    latitudeLink: Optional[str] = None
    images: Optional[list[str]] = None
    documents: Optional[list[str]] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None

class WarehouseResponse(WarehouseBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

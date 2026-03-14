from pydantic import BaseModel, ConfigDict
from typing import Optional

class WarehouseBase(BaseModel):
    name: str
    manager: str
    contact: str
    location: str
    status: str
    createdDate: str

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    manager: Optional[str] = None
    contact: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None

class WarehouseResponse(WarehouseBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

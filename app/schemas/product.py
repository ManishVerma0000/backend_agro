from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    code: str
    name: str
    category: str
    hsn: str
    basePrice: str
    b2b: str
    status: str
    createdDate: str
    imageUrl: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    hsn: Optional[str] = None
    basePrice: Optional[str] = None
    b2b: Optional[str] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None
    imageUrl: Optional[str] = None

class ProductResponse(ProductBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

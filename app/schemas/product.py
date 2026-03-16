from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class ProductBase(BaseModel):
    code: str
    name: str
    categoryId: Optional[str] = ""
    subcategoryId: Optional[str] = ""
    category: Optional[str] = "" # for legacy data
    hsn: str
    basePrice: str
    b2b: str
    status: str
    createdDate: str
    imageUrl: Optional[str] = None
    partcode: Optional[str] = None
    gstRate: Optional[str] = None
    mrp: Optional[str] = None
    baseUnit: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    organic: Optional[str] = None
    origin: Optional[str] = None
    shelfLife: Optional[str] = None
    storage: Optional[str] = None
    variations: Optional[List[Dict[str, Any]]] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    categoryId: Optional[str] = None
    subcategoryId: Optional[str] = None
    hsn: Optional[str] = None
    basePrice: Optional[str] = None
    b2b: Optional[str] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None
    imageUrl: Optional[str] = None
    partcode: Optional[str] = None
    gstRate: Optional[str] = None
    mrp: Optional[str] = None
    baseUnit: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    organic: Optional[str] = None
    origin: Optional[str] = None
    shelfLife: Optional[str] = None
    storage: Optional[str] = None
    variations: Optional[List[Dict[str, Any]]] = None

class ProductResponse(ProductBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

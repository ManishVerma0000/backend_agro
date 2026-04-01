from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class MobileProductResponse(BaseModel):
    id: str
    productId: str
    name: str
    category: Optional[str] = None
    categoryId: Optional[str] = None
    subcategoryId: Optional[str] = None
    hsnCode: Optional[str] = None
    basePrice: Optional[float] = 0.0
    mrp: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    baseUnit: Optional[str] = None
    availableStock: Optional[int] = 0
    status: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)

class MobileCategory(BaseModel):
    id: str
    name: str
    imageUrl: Optional[str] = None

class MobileSubcategory(BaseModel):
    id: str
    name: str
    categoryId: Optional[str] = None
    hsnCodesCount: Optional[int] = 0
    status: Optional[str] = None
    imageUrl: Optional[str] = None

class MobileCategoryFull(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    imageUrl: Optional[str] = None
    subcategories: List[MobileSubcategory] = []

class MobileBanner(BaseModel):
    id: str
    imageUrl: str
    title: Optional[str] = None
    actionUrl: Optional[str] = None

class MobileHomeResponse(BaseModel):
    banners: List[MobileBanner]
    categories: List[MobileCategory]
    quickOrders: List[MobileProductResponse]

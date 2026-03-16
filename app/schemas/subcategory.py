from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class HsnCode(BaseModel):
    code: str
    gst: str
    description: Optional[str] = None

class SubcategoryBase(BaseModel):
    name: str
    categoryId: Optional[str] = ""
    category: Optional[str] = "" # for legacy data
    hsnCodesCount: int
    status: str
    createdDate: str
    imageUrl: Optional[str] = None
    hsnCodes: List[HsnCode] = []

class SubcategoryCreate(SubcategoryBase):
    pass

class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    categoryId: Optional[str] = None
    hsnCodesCount: Optional[int] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None
    imageUrl: Optional[str] = None
    hsnCodes: Optional[List[HsnCode]] = None

class SubcategoryResponse(SubcategoryBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

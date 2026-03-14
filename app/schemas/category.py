from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: str
    priority: int
    status: str
    createdDate: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    createdDate: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: str

    model_config = ConfigDict(populate_by_name=True)

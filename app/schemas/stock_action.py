from pydantic import BaseModel, ConfigDict
from typing import Optional

class StockActionBase(BaseModel):
    label: str
    iconName: str
    bg: str
    text: str
    hover: str
    border: Optional[str] = ""

class StockActionCreate(StockActionBase):
    pass

class StockActionResponse(StockActionBase):
    id: str
    
    model_config = ConfigDict(populate_by_name=True)

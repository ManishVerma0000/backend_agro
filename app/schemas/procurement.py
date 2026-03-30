from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class SupplierBase(BaseModel):
    name: str
    contactPerson: str
    email: str
    phone: str
    address: Optional[str] = None
    status: str = "Active"

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contactPerson: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None

class SupplierResponse(SupplierBase):
    id: str
    model_config = ConfigDict(populate_by_name=True)


class PurchaseOrderBase(BaseModel):
    poNumber: str
    supplierId: str
    supplierName: str
    orderDate: str
    expectedDelivery: str
    totalAmount: float
    status: str # 'Pending', 'Partially Received', 'Received', 'Cancelled'
    items: List[Dict[str, Any]] # Array of { productId, productName, quantity, unitPrice }

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(BaseModel):
    expectedDelivery: Optional[str] = None
    totalAmount: Optional[float] = None
    status: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: str
    model_config = ConfigDict(populate_by_name=True)

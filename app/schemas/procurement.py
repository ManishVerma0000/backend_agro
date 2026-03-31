from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class SupplierBase(BaseModel):
    name: str
    contactPerson: str
    email: str
    phone: str
    address: Optional[str] = None
    location: str
    gstNumber: Optional[str] = None
    status: str = "Active"
    
    # Tracking metrics (defaults to 0 for a new supplier)
    products: int = 0
    poCount: int = 0
    totalAmount: float = 0.0
    pendingAmount: float = 0.0
    paidAmount: float = 0.0

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contactPerson: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    gstNumber: Optional[str] = None
    status: Optional[str] = None
    
    products: Optional[int] = None
    poCount: Optional[int] = None
    totalAmount: Optional[float] = None
    pendingAmount: Optional[float] = None
    paidAmount: Optional[float] = None

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

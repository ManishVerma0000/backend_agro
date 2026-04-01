from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerAddressCreate, CustomerAddressUpdate
from datetime import datetime

async def create_customer(customer_in: CustomerCreate) -> dict:
    db = get_db()
    cust_dict = customer_in.model_dump()
    cust_dict["createdDate"] = datetime.utcnow()
    result = await db["customers"].insert_one(cust_dict)
    cust_dict["id"] = str(cust_dict.pop("_id"))
    return cust_dict

async def get_customer_by_mobile(mobile: str) -> Optional[dict]:
    db = get_db()
    customer = await db["customers"].find_one({"mobileNumber": mobile})
    if customer:
        customer["id"] = str(customer.pop("_id"))
    return customer

async def get_customer(customer_id: str) -> Optional[dict]:
    db = get_db()
    customer = await db["customers"].find_one({"_id": ObjectId(customer_id)})
    if customer:
        customer["id"] = str(customer.pop("_id"))
    return customer

# --- Addresses CRUD ---

async def create_customer_address(customer_id: str, address_in: CustomerAddressCreate) -> dict:
    db = get_db()
    addr_dict = address_in.model_dump()
    addr_dict["customerId"] = customer_id
    addr_dict["createdAt"] = datetime.utcnow()
    
    # If it is set as default, we need to unset any existing default address for this customer
    if addr_dict.get("isDefault"):
        await db["customer_addresses"].update_many(
            {"customerId": customer_id}, 
            {"$set": {"isDefault": False}}
        )

    result = await db["customer_addresses"].insert_one(addr_dict)
    addr_dict["id"] = str(addr_dict.pop("_id"))
    return addr_dict

async def get_customer_addresses(customer_id: str) -> List[dict]:
    db = get_db()
    cursor = db["customer_addresses"].find({"customerId": customer_id}).sort("createdAt", -1)
    addresses = []
    async for addr in cursor:
        addr["id"] = str(addr.pop("_id"))
        addresses.append(addr)
    return addresses

async def get_customer_address(address_id: str) -> Optional[dict]:
    db = get_db()
    addr = await db["customer_addresses"].find_one({"_id": ObjectId(address_id)})
    if addr:
        addr["id"] = str(addr.pop("_id"))
    return addr

async def update_customer_address(customer_id: str, address_id: str, address_in: CustomerAddressUpdate) -> Optional[dict]:
    db = get_db()
    update_data = address_in.model_dump(exclude_unset=True)
    
    if update_data.get("isDefault"):
        # Unset others
        await db["customer_addresses"].update_many(
            {"customerId": customer_id, "_id": {"$ne": ObjectId(address_id)}},
            {"$set": {"isDefault": False}}
        )

    if update_data:
        await db["customer_addresses"].update_one(
            {"_id": ObjectId(address_id), "customerId": customer_id},
            {"$set": update_data}
        )
    return await get_customer_address(address_id)

async def delete_customer_address(customer_id: str, address_id: str) -> bool:
    db = get_db()
    result = await db["customer_addresses"].delete_one({"_id": ObjectId(address_id), "customerId": customer_id})
    return result.deleted_count > 0

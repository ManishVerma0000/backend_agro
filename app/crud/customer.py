from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerAddressCreate, CustomerAddressUpdate
from datetime import datetime, timedelta

async def get_all_customers() -> List[dict]:
    db = get_db()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    now = datetime.utcnow()
    
    pipeline = [
        {
            "$addFields": {
                "customerObjectId": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "mobile_orders",
                "localField": "customerObjectId",
                "foreignField": "customerId",
                "as": "orders"
            }
        },
        {
            "$addFields": {
                "totalOrders": {"$size": "$orders"},
                "totalSpent": {"$sum": "$orders.grandTotal"},
                "lastOrderDate": {"$max": "$orders.createdAt"},
                "thirtyDaysOrders": {
                    "$filter": {
                        "input": "$orders",
                        "as": "order",
                        "cond": {"$gte": ["$$order.createdAt", thirty_days_ago]}
                    }
                }
            }
        },
        {
            "$addFields": {
                "thirtyDaysOrderValue": {"$sum": "$thirtyDaysOrders.grandTotal"},
                "daysSinceLastOrder": {
                    "$cond": [
                        {"$eq": ["$lastOrderDate", None]},
                        9999,
                        {"$divide": [
                            {"$subtract": [now, "$lastOrderDate"]},
                            1000 * 60 * 60 * 24
                        ]}
                    ]
                }
            }
        },
        {
            "$addFields": {
                "customerType": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$totalOrders", 0]}, "then": "New"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 100000]}, "then": "High"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 50000]}, "then": "Medium"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 1500]}, "then": "Low"}
                        ],
                        "default": "New" # If < 1500 but > 0 orders, we can make them Low or New. Making Low is better as per instructions "0 order = New". Let's put Low.
                    }
                },
                "customerStatus": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lte": ["$daysSinceLastOrder", 3.0]}, "then": "Active"},
                            {"case": {"$lte": ["$daysSinceLastOrder", 14.0]}, "then": "At Risk"},
                        ],
                        "default": "Inactive"
                     }
                }
            }
        },
        {
            "$project": {
                "orders": 0,
                "customerObjectId": 0,
                "thirtyDaysOrders": 0,
                "daysSinceLastOrder": 0
            }
        }
    ]

    cursor = db["customers"].aggregate(pipeline)
    customers = []
    async for cust in cursor:
        cust["id"] = str(cust.pop("_id"))
        
        # Override the defaults if needed if it was unhandled (e.g. totalOrders > 0 but < 1500)
        if cust.get("customerType") == "New" and cust.get("totalOrders", 0) > 0:
            cust["customerType"] = "Low"
            
        customers.append(cust)
    return customers

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

async def get_customer_with_stats(customer_id: str) -> Optional[dict]:
    db = get_db()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    now = datetime.utcnow()

    # Robust ID handling
    possible_ids = [customer_id]
    try:
        possible_ids.append(ObjectId(customer_id))
    except:
        pass

    pipeline = [
        {"$match": {"_id": {"$in": possible_ids}}},
        {
            "$addFields": {
                "customerObjectId": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "mobile_orders",
                "localField": "customerObjectId",
                "foreignField": "customerId",
                "as": "orders"
            }
        },
        {
            "$addFields": {
                "totalOrders": {"$size": "$orders"},
                "totalSpent": {"$sum": "$orders.grandTotal"},
                "lastOrderDate": {"$max": "$orders.createdAt"},
                "thirtyDaysOrders": {
                    "$filter": {
                        "input": "$orders",
                        "as": "order",
                        "cond": {"$gte": ["$$order.createdAt", thirty_days_ago]}
                    }
                }
            }
        },
        {
            "$addFields": {
                "thirtyDaysOrderValue": {"$sum": "$thirtyDaysOrders.grandTotal"},
                "daysSinceLastOrder": {
                    "$cond": [
                        {"$eq": ["$lastOrderDate", None]},
                        9999,
                        {"$divide": [
                            {"$subtract": [now, "$lastOrderDate"]},
                            1000 * 60 * 60 * 24
                        ]}
                    ]
                }
            }
        },
        {
            "$addFields": {
                "customerType": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$totalOrders", 0]}, "then": "New"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 100000]}, "then": "High"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 50000]}, "then": "Medium"},
                            {"case": {"$gte": ["$thirtyDaysOrderValue", 1500]}, "then": "Low"}
                        ],
                        "default": "New"
                    }
                },
                "customerStatus": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lte": ["$daysSinceLastOrder", 3.0]}, "then": "Active"},
                            {"case": {"$lte": ["$daysSinceLastOrder", 14.0]}, "then": "At Risk"},
                        ],
                        "default": "Inactive"
                     }
                }
            }
        },
        {
            "$project": {
                "orders": 0,
                "customerObjectId": 0,
                "thirtyDaysOrders": 0,
                "daysSinceLastOrder": 0
            }
        }
    ]

    cursor = db["customers"].aggregate(pipeline)
    async for cust in cursor:
        cust["id"] = str(cust.pop("_id"))
        if cust.get("customerType") == "New" and cust.get("totalOrders", 0) > 0:
            cust["customerType"] = "Low"
        return cust
    return None

async def update_customer(customer_id: str, customer_in: CustomerUpdate) -> Optional[dict]:
    db = get_db()
    update_data = customer_in.model_dump(exclude_unset=True)
    if update_data:
        await db["customers"].update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": update_data}
        )
    return await get_customer(customer_id)

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

from typing import List
from bson import ObjectId
from app.db.session import get_db


async def get_customers_by_warehouse(warehouse_id: str) -> List[dict]:
    """
    Returns all unique customers who have placed at least one order
    to the given warehouse, enriched with order stats.
    """
    db = get_db()

    pipeline = [
        # 1. Match orders for this warehouse
        {"$match": {"warehouseId": warehouse_id}},

        # 2. Group by customer to get order stats
        {
            "$group": {
                "_id": "$customerId",
                "totalOrders": {"$sum": 1},
                "totalSpent": {"$sum": "$grandTotal"},
                "lastOrderDate": {"$max": "$createdAt"},
            }
        },

        # 3. Lookup customer details
        {
            "$addFields": {
                "customerObjectId": {"$toObjectId": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerObjectId",
                "foreignField": "_id",
                "as": "customer_info"
            }
        },
        {"$unwind": {"path": "$customer_info", "preserveNullAndEmptyArrays": True}},

        # 4. Shape output
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$customerObjectId"},
                "shopName": {"$ifNull": ["$customer_info.shopName", "Unknown Shop"]},
                "ownerName": {"$ifNull": ["$customer_info.ownerName", "Unknown"]},
                "mobileNumber": {"$ifNull": ["$customer_info.mobileNumber", "N/A"]},
                "city": {"$ifNull": ["$customer_info.city", "N/A"]},
                "shopType": {"$ifNull": ["$customer_info.shopType", "N/A"]},
                "status": {"$ifNull": ["$customer_info.status", "Active"]},
                "createdDate": {"$ifNull": ["$customer_info.createdDate", None]},
                "totalOrders": 1,
                "totalSpent": 1,
                "lastOrderDate": 1,
            }
        },

        {"$sort": {"lastOrderDate": -1}}
    ]

    cursor = db["mobile_orders"].aggregate(pipeline)
    customers = []
    async for c in cursor:
        customers.append(c)
    return customers

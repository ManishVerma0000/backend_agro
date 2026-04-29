import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_api():
    mongo_uri = "mongodb+srv://manishvermajiyofresh:LerrNVoPndaaW0c2@jiofresh.dq6a869.mongodb.net/nestjs_demo?retryWrites=true&w=majority&appName=HealthAxis"
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    
    warehouse_id = "69b82ccf3709f6cca0ec8c41"
    customer_id = "69d203949e99fc8ccfc8c024"
    
    print(f"--- Debugging for Warehouse: {warehouse_id}, Customer: {customer_id} ---")
    
    # 1. Check Warehouse
    try:
        w = await db['warehouses'].find_one({"_id": ObjectId(warehouse_id)})
        print(f"Warehouse Found: {True if w else False}")
        if w: print(f"Warehouse Status: {w.get('status')}")
    except:
        print("Warehouse ID is not a valid ObjectId")

    # 2. Check Customer Orders
    order_count = await db["mobile_orders"].count_documents({"customerId": customer_id})
    print(f"Customer Order Count: {order_count}")
    
    # 3. Check Warehouse Products (Direct)
    wp_count = await db["warehouse_products"].count_documents({"warehouseId": warehouse_id, "status": "Active"})
    print(f"Active Warehouse Products Count: {wp_count}")
    
    # 4. Check Global Popular Items for this Warehouse
    popular_pipeline = [
        {"$match": {"warehouseId": warehouse_id}},
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.productId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    popular_items = []
    async for doc in db["mobile_orders"].aggregate(popular_pipeline):
        popular_items.append(doc)
    print(f"Popular Items Count: {len(popular_items)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_api())

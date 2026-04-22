import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run():
    load_dotenv()
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "agro_hub")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connecting to {mongo_url}, DB: {db_name}")
    
    # Check distinct warehouse IDs in orders
    distinct_warehouses = await db['mobile_orders'].distinct("warehouseId")
    print(f"Distinct Warehouse IDs in orders: {distinct_warehouses}")
    
    # Check total orders
    count = await db['mobile_orders'].count_documents({})
    print(f"Total orders: {count}")
    
    # Check if our specific ID exists in orders
    target_id = "69de6c2385dc43cd3375ab8d"
    target_count = await db['mobile_orders'].count_documents({"warehouseId": target_id})
    print(f"Orders for target ID {target_id}: {target_count}")
    
    # Sample order to see structure
    sample = await db['mobile_orders'].find_one({})
    if sample:
        print(f"Sample Order WarehouseId type: {type(sample.get('warehouseId'))}")
        print(f"Sample Order WarehouseId value: '{sample.get('warehouseId')}'")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

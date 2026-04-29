import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def find_ids():
    # Fetch MongoDB URI from .env if possible, else default
    mongo_uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017/flick")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    
    warehouse = await db['warehouses'].find_one({"status": "Active"})
    order = await db['mobile_orders'].find_one()
    
    print(f"WAREHOUSE_ID: {str(warehouse['_id']) if warehouse else 'None'}")
    print(f"CUSTOMER_ID: {order['customerId'] if order else 'None'}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(find_ids())

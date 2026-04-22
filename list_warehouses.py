import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run():
    load_dotenv()
    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DATABASE_NAME", "fastapi_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Listing all warehouses in {db_name}:")
    cursor = db['warehouses'].find({}, {"name": 1, "email": 1})
    async for w in cursor:
        print(f"Name: {w.get('name')}, Email: {w.get('email')}, ID: {w.get('_id')}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

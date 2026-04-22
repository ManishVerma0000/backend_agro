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
    
    print(f"Warehouses in {db_name}:")
    cursor = db['warehouses'].find()
    async for w in cursor:
        print(f"ID: {w['_id']}, Name: {w.get('name')}, Email: {w.get('email')}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

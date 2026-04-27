import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import pprint

async def run():
    load_dotenv()
    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DATABASE_NAME", "fastapi_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    cursor = db['warehouses'].find()
    async for w in cursor:
        pprint.pprint(w)
        print("-" * 20)
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

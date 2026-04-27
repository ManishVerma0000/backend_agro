import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run():
    load_dotenv()
    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DATABASE_NAME", "fastapi_db")
    
    print(f"Connecting to {mongo_url}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Inspecting one warehouse in {db_name}:")
    warehouse = await db['warehouses'].find_one()
    if warehouse:
        import pprint
        pprint.pprint(warehouse)
    else:
        print("No warehouses found.")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

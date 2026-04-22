import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

async def run():
    load_dotenv()
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "agro_hub")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connecting to {mongo_url}, DB: {db_name}")
    
    warehouses = await db['warehouses'].find().to_list(None)
    print("--- WAREHOUSES ---")
    for w in warehouses:
        print(f"ID: {w['_id']}, Name: {w.get('name')}, Email: {w.get('email')}, OTP: {w.get('otp')}")
        
    products = await db['products'].find().to_list(None)
    print("\n--- PRODUCTS COUNT ---")
    print(len(products))
    
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

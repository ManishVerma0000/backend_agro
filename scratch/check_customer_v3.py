import asyncio
import os
import sys
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

async def check_customer():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client["fastapi_db"]
    # Let's find ANY customer with addresses
    c = await db["customers"].find_one({"addresses": {"$exists": True, "$ne": []}})
    if c:
        print(f"Customer: {c.get('shopName')}")
        print(f"Addresses: {c.get('addresses')}")
    else:
        print("No customer with addresses found")
    client.close()

if __name__ == "__main__":
    asyncio.run(check_customer())

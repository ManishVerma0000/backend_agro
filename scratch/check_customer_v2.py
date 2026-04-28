import asyncio
import os
import sys
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

async def check_customer():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client["fastapi_db"]
    customer_id = "69cd628910c53f3ac1127c9c"
    c = await db["customers"].find_one({"_id": ObjectId(customer_id)})
    if c:
        print(f"Customer: {c.get('shopName')}")
        print(f"Addresses: {c.get('addresses')}")
    else:
        print("Customer not found in fastapi_db")
    client.close()

if __name__ == "__main__":
    asyncio.run(check_customer())

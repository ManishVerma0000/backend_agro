import asyncio
import os
import sys
from bson import ObjectId

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from app.db.session import get_db, connect_to_mongo

async def check_customer():
    await connect_to_mongo()
    db = get_db()
    customer_id = "69cd628910c53f3ac1127c9c"
    c = await db["customers"].find_one({"_id": ObjectId(customer_id)})
    if c:
        print(f"Customer: {c.get('shopName')}")
        addresses = c.get('addresses', [])
        for addr in addresses:
            print(f"Address: {addr.get('location')}")
            print(f"Lat: {addr.get('lat')}, Long: {addr.get('long')}")
    else:
        print("Customer not found")

if __name__ == "__main__":
    asyncio.run(check_customer())

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from app.db.session import get_db

async def check_warehouses():
    db = get_db()
    print("Checking warehouses...")
    cursor = db["warehouses"].find({"status": "Active"})
    async for w in cursor:
        print(f"Name: {w.get('name')}, Location: {w.get('location')}, ID: {w.get('_id')}")

if __name__ == "__main__":
    asyncio.run(check_warehouses())

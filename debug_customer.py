import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from app.db.session import connect_to_mongo, get_db
from bson import ObjectId

async def test():
    try:
        await connect_to_mongo()
        db = get_db()
        
        target_id = "69cd62e7d0750cba9f50d7a6"
        print(f"Checking for customer ID: {target_id}")
        
        # Test direct find
        cust = await db["customers"].find_one({"_id": ObjectId(target_id)})
        print(f"Direct find result: {'Found' if cust else 'Not Found'}")
        
        # Test our aggregation logic
        from app.crud.customer import get_customer_with_stats
        cust_stats = await get_customer_with_stats(target_id)
        print(f"get_customer_with_stats result: {'Found' if cust_stats else 'Not Found'}")
        
        if cust_stats:
            print(f"Stats: {cust_stats}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close connection if possible
        pass

if __name__ == "__main__":
    asyncio.run(test())

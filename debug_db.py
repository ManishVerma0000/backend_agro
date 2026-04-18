import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from app.db.session import connect_to_mongo, get_db
from bson import ObjectId

async def test():
    await connect_to_mongo()
    db = get_db()
    count = await db["customers"].count_documents({})
    print(f"Total customers: {count}")
    
    first_cust = await db["customers"].find_one()
    if first_cust:
        print(f"First customer ID: {first_cust['_id']}")
        print(f"First customer: {first_cust}")
    
    # Test our aggregation logic
    if first_cust:
        customer_id = str(first_cust['_id'])
        print(f"Testing aggregation for ID: {customer_id}")
        
        pipeline = [
            {"$match": {"_id": ObjectId(customer_id)}}
        ]
        cursor = db["customers"].aggregate(pipeline)
        results = []
        async for r in cursor:
            results.append(r)
        print(f"Aggregation results found: {len(results)}")
        if results:
            print(f"Aggregation result: {results[0]}")

asyncio.run(test())

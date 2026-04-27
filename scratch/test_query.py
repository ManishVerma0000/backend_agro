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
    
    lat = 28.3901952
    lon = 77.3423104
    
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lon, lat]},
                "distanceField": "distance",
                "spherical": True,
                "query": {"status": "Active"},
                "maxDistance": 10000
            }
        },
        {"$limit": 1}
    ]
    
    cursor = db["warehouses"].aggregate(pipeline)
    async for w in cursor:
        print(f"Found nearest warehouse: {w.get('name')} at distance {w.get('distance')}m")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

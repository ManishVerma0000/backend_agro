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
    
    print("Updating warehouses with location_geo field...")
    cursor = db['warehouses'].find()
    async for w in cursor:
        lat_link = w.get("latitudeLink")
        if lat_link and "," in lat_link:
            try:
                parts = lat_link.split(",")
                if len(parts) >= 2:
                    lat_str = parts[0].strip()
                    lon_str = parts[1].strip()
                    if lat_str and lon_str:
                        lat = float(lat_str)
                        lon = float(lon_str)
                        print(f"Updating warehouse {w.get('name')} with coordinates: {lat}, {lon}")
                        await db['warehouses'].update_one(
                            {"_id": w["_id"]},
                            {"$set": {"location_geo": {"type": "Point", "coordinates": [lon, lat]}}}
                        )
                    else:
                        print(f"Skipping warehouse {w.get('name')} due to empty coordinates in latitudeLink")
            except Exception as e:
                print(f"Error parsing coordinates for warehouse {w.get('name')}: {e}")
        else:
            print(f"Skipping warehouse {w.get('name')} due to missing or invalid latitudeLink: {lat_link}")
    
    print("Creating 2dsphere index on location_geo...")
    try:
        await db['warehouses'].create_index([("location_geo", "2dsphere")])
        print("Index created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
import sys
from bson import ObjectId

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from app.db.session import get_db, connect_to_mongo

async def update_warehouse():
    await connect_to_mongo()
    db = get_db()
    warehouse_id = "69b82ccf3709f6cca0ec8c41"
    new_lat = 28.55121656724048
    new_lon = 77.34540030466398
    
    res = await db['warehouses'].update_one(
        {'_id': ObjectId(warehouse_id)}, 
        {'$set': {
            'location_geo': {'type': 'Point', 'coordinates': [new_lon, new_lat]},
            'latitudeLink': f"{new_lat},{new_lon}"
        }}
    )
    if res.modified_count > 0:
        print("Warehouse location updated successfully.")
    else:
        print("Warehouse location not updated (already set or not found).")

if __name__ == "__main__":
    asyncio.run(update_warehouse())

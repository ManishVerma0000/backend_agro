import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from app.db.session import connect_to_mongo, get_db
from app.crud.mobile_order import get_customer_orders
from bson import ObjectId

async def run():
    await connect_to_mongo()
    db = get_db()
    
    customer_id = "69d280b2a529121b4de6b137"
    print("Fetching customer orders history from backend API crud...")
    res = await get_customer_orders(customer_id, skip=0, limit=10)
    
    print("\n--- PAST ORDERS DYNAMIC WAREHOUSE ID VERIFICATION ---")
    for order in res["items"]:
        oid = order["id"]
        stored_order = await db["mobile_orders"].find_one({"_id": ObjectId(oid)}) or {}
        db_wh_id = stored_order.get("warehouseId")
        returned_wh_id = order.get("warehouseId")
        
        addr = order.get("deliveryAddress", {})
        addr_location = addr.get("location")
        lat = addr.get("lat")
        lon = addr.get("long") or addr.get("lon") or addr.get("lng")
        
        # Look up warehouse names
        db_wh = await db["warehouses"].find_one({"_id": ObjectId(db_wh_id)}) if db_wh_id else None
        db_wh_name = db_wh.get("name") if db_wh else "None/Unknown"
        
        ret_wh = await db["warehouses"].find_one({"_id": ObjectId(returned_wh_id)}) if returned_wh_id else None
        ret_wh_name = ret_wh.get("name") if ret_wh else "None/Unknown"
        
        print(f"\nOrder ID: {oid}")
        print(f"  Address: {addr_location} (lat={lat}, long={lon})")
        print(f"  DB Stored Warehouse: {db_wh_name} ({db_wh_id})")
        print(f"  Returned Warehouse  : {ret_wh_name} ({returned_wh_id})")
        
        # Assertions
        if "Faridabad" in str(addr_location):
            # Closest active warehouse should be Faridabad Warehouse
            assert returned_wh_id == "6a02112bf3b1c91668655775", "Error: Expected Faridabad Warehouse ID"
            print("  [SUCCESS] Correctly resolved to closest active Faridabad Warehouse")
        elif "Rewari" in str(addr_location):
            # Closest active warehouse should be Narnaul Warehouse
            assert returned_wh_id == "69fa29842cb398c1d1bf5871", "Error: Expected Narnaul Warehouse ID"
            print("  [SUCCESS] Correctly resolved to closest active Narnaul Warehouse")

if __name__ == "__main__":
    asyncio.run(run())

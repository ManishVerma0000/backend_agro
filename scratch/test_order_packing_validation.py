import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import connect_to_mongo, get_db
from app.crud.mobile_order import place_order, start_packing
from app.schemas.mobile_order import MobileOrderCreate

async def main():
    print("--- Starting Order Packing Stock-Out Validation Test ---")
    
    # 1. Setup DB Connection
    await connect_to_mongo()
    db = get_db()
    
    # 2. Get/Create a mock product and warehouse
    wp = await db["warehouse_products"].find_one()
    if not wp:
        print("No warehouse products found in DB. Initializing mock product/warehouse.")
        # Setup mock product
        prod_res = await db["products"].insert_one({
            "name": "Test Apple Brand",
            "category": "Fruits",
            "price": 100.0,
            "unit": "Kg"
        })
        product_id = str(prod_res.inserted_id)
        warehouse_id = "test-warehouse-wms-123"
        
        # Setup warehouse product
        await db["warehouse_products"].insert_one({
            "productId": product_id,
            "warehouseId": warehouse_id,
            "currentStock": 100,
            "availableStock": 100,
            "reservedStock": 0,
            "basePrice": 90.0
        })
        wp = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
    
    product_id = wp["productId"]
    warehouse_id = wp["warehouseId"]
    
    print(f"Target Product ID: {product_id}")
    print(f"Target Warehouse ID: {warehouse_id}")
    
    # 3. Artificially set availableStock to 0 to simulate stock-out (or deficit)
    print("\nForcefully setting warehouse available stock to 0 to trigger shortage...")
    await db["warehouse_products"].update_one(
        {"productId": product_id, "warehouseId": warehouse_id},
        {"$set": {"availableStock": 0, "currentStock": 5, "reservedStock": 5}}
    )
    
    # 4. Create mock customer
    customer = await db["customers"].find_one()
    customer_id = str(customer["_id"]) if customer else "mock-customer-123"
    
    # 5. Place an order for 10 units (which exceeds available Stock)
    order_in = MobileOrderCreate(
        customerId=customer_id,
        warehouseId=warehouse_id,
        subtotal=100.0,
        deliveryFee=10.0,
        grandTotal=110.0,
        paymentMethod="Cash",
        items=[
            {
                "productId": product_id,
                "productName": "Test Apple Brand",
                "quantity": 10,
                "unitPrice": 10.0
            }
        ]
    )
    
    print("Placing order for 10 units (shortage condition)...")
    order = await place_order(order_in)
    order_id = order["id"]
    print(f"Placed Order successfully! ID: {order_id}, Status: {order.get('status')}")
    
    # Verify new warehouse stock states (available stock goes negative due to reservation)
    wp_after_order = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
    print(f"Stocks after Order Placement -> Current: {wp_after_order.get('currentStock')}, Available: {wp_after_order.get('availableStock')}, Reserved: {wp_after_order.get('reservedStock')}")
    
    # 6. Attempt to pack (start_packing) and expect the ValueError
    print("\nAttempting to start packing...")
    try:
        await start_packing(order_id)
        print("[FAIL] start_packing completed successfully without raising error!")
        assert False, "Should have raised ValueError!"
    except ValueError as e:
        print(f"[PASS] Successfully caught expected ValueError!")
        print(f"Error Message: {str(e)}")
        assert str(e) == "Items stock is not available or partially available", f"Mismatch error string: {str(e)}"
        print("[PASS] Exact error message match validated successfully!")
        
    print("\n--- All tests completed successfully! ---")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

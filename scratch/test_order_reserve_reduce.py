import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import connect_to_mongo, get_db
from app.crud.mobile_order import place_order, bulk_update_status
from app.schemas.mobile_order import MobileOrderCreate

async def main():
    print("--- Starting Order Stock Allocation & Reduction Test ---")
    
    # 1. Setup DB Connection using core connection session
    await connect_to_mongo()
    db = get_db()
    
    # 2. Get/Create a mock product and warehouse
    # Let's find an existing warehouse product to run our tests cleanly
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
    print(f"Initial Stocks -> Current: {wp.get('currentStock')}, Available: {wp.get('availableStock')}, Reserved: {wp.get('reservedStock')}")
    
    initial_current = wp.get("currentStock", 0)
    initial_available = wp.get("availableStock", 0)
    initial_reserved = wp.get("reservedStock", 0)
    
    # 3. Create mock customer
    customer = await db["customers"].find_one()
    customer_id = str(customer["_id"]) if customer else "mock-customer-123"
    
    # 4. Create and Place a mock order
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
    
    print("\nPlacing order for 10 units...")
    order = await place_order(order_in)
    order_id = order["id"]
    print(f"Placed Order successfully! ID: {order_id}, Status: {order.get('status')}")
    
    # Verify reservation in DB
    wp_after_order = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
    print(f"Stocks after Order Placement -> Current: {wp_after_order.get('currentStock')}, Available: {wp_after_order.get('availableStock')}, Reserved: {wp_after_order.get('reservedStock')}")
    
    assert wp_after_order.get("reservedStock") == initial_reserved + 10, "Reserved stock should increment by 10!"
    assert wp_after_order.get("availableStock") == initial_available - 10, "Available stock should decrement by 10!"
    assert wp_after_order.get("currentStock") == initial_current, "Current stock should remain unchanged!"
    print("[PASS] Order Stock Reservation passed successfully!")
    
    # 5. Dispatch Order (Set Status to Out for Delivery)
    print("\nUpdating order status to 'Out for Delivery'...")
    success = await bulk_update_status([order_id], "Out for Delivery")
    print(f"Status update return: {success}")
    
    # Verify reduction in DB
    wp_after_dispatch = await db["warehouse_products"].find_one({"productId": product_id, "warehouseId": warehouse_id})
    print(f"Stocks after Dispatch -> Current: {wp_after_dispatch.get('currentStock')}, Available: {wp_after_dispatch.get('availableStock')}, Reserved: {wp_after_dispatch.get('reservedStock')}")
    
    assert wp_after_dispatch.get("currentStock") == initial_current - 10, "Current stock should decrement by 10!"
    assert wp_after_dispatch.get("reservedStock") == initial_reserved, "Reserved stock should decrement back to initial!"
    assert wp_after_dispatch.get("availableStock") == initial_available - 10, "Available stock should remain decremented!"
    print("[PASS] Order Stock Reduction passed successfully!")
    
    # 6. Verify Inventory Movement History
    movement = await db["inventory_movements"].find_one({"productId": product_id, "type": "Order Fulfillment"})
    if movement:
        print(f"[PASS] Found Inventory Movement: Type: {movement.get('type')}, Quantity: {movement.get('quantity')}, Reference: {movement.get('reference')}")
    else:
        print("[FAIL] Inventory Movement log NOT found!")
        
    print("\n--- All tests completed successfully! ---")

if __name__ == "__main__":
    # Workaround for event loop issues in Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

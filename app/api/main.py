from fastapi import APIRouter
from app.api.routes import users, auth, upload, categories, subcategories, products, warehouses, orders, dashboard, inventory, procurement, warehouse_products, stock_action, inventory_movements, mobile_auth, mobile_address, mobile, mobile_cart, mobile_order

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(subcategories.router, prefix="/subcategories", tags=["subcategories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(warehouse_products.router, prefix="/warehouse-products", tags=["warehouse-products"])
api_router.include_router(stock_action.router, prefix="/stock-actions", tags=["stock-actions"])
api_router.include_router(inventory_movements.router, prefix="/inventory-movements", tags=["inventory-movements"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(procurement.router, prefix="/procurement", tags=["procurement"])

# Mobile App Routes
api_router.include_router(mobile_auth.router, prefix="/mobile/auth", tags=["mobile-auth"])
api_router.include_router(mobile_address.router, prefix="/mobile/addresses", tags=["mobile-address"])
api_router.include_router(mobile.router, prefix="/mobile", tags=["mobile"])
api_router.include_router(mobile_cart.router, prefix="/mobile/cart", tags=["mobile-cart"])
api_router.include_router(mobile_order.router, prefix="/mobile/orders", tags=["mobile-orders"])

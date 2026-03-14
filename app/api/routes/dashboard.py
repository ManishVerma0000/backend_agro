from fastapi import APIRouter
from app.db.session import get_db

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats():
    db = get_db()
    cat_count = await db["categories"].count_documents({})
    subcat_count = await db["subcategories"].count_documents({})
    prod_count = await db["products"].count_documents({})
    warehouse_count = await db["warehouses"].count_documents({})
    
    return {
        "categories": cat_count,
        "subcategories": subcat_count,
        "products": prod_count,
        "warehouses": warehouse_count,
        "b2bOrders": 452000,
        "b2cOrders": 128500,
        "activeBuyers": 2341
    }

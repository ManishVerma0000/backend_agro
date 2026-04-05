from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db

async def get_mobile_products(warehouse_id: str, category_id: Optional[str] = None, subcategory_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    
    match_query = {
        "warehouseId": warehouse_id,
        "status": "Active" # Only active warehouse products
    }
    
    pipeline = [
        {"$match": match_query},
        {"$addFields": {"productObjectId": {"$toObjectId": "$productId"}}},
        {
            "$lookup": {
                "from": "products",
                "localField": "productObjectId",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        # Filter active master products
        {"$match": {"product_info.status": "Active"}},
        {
            "$addFields": {
                "categoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.categoryId", ""]}, {"$ne": ["$product_info.categoryId", None]}]},
                        {"$toObjectId": "$product_info.categoryId"},
                        None
                    ]
                },
                "subcategoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.subcategoryId", ""]}, {"$ne": ["$product_info.subcategoryId", None]}]},
                        {"$toObjectId": "$product_info.subcategoryId"},
                        None
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "categoryObjectId",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "subcategories",
                "localField": "subcategoryObjectId",
                "foreignField": "_id",
                "as": "subcategory_info"
            }
        },
        {"$unwind": {"path": "$subcategory_info", "preserveNullAndEmptyArrays": True}}
    ]

    # Optional Category Filter
    if category_id:
        pipeline.append({"$match": {"product_info.categoryId": category_id}})

    # Optional Subcategory Filter
    if subcategory_id:
        pipeline.append({"$match": {"product_info.subcategoryId": subcategory_id}})

    # Projection
    pipeline.append({
        "$project": {
            "_id": 1,
            "productId": 1,
            "availableStock": 1,
            "status": 1,
            "basePrice": {
                "$cond": [
                    {"$and": [{"$ne": ["$basePrice", None]}, {"$gt": ["$basePrice", 0]}]},
                    "$basePrice", 
                    {"$toDouble": "$product_info.basePrice"}
                ]
            },
            "name": "$product_info.name",
            "category": "$category_info.name",
            "categoryId": "$product_info.categoryId",
            "subcategoryId": "$product_info.subcategoryId",
            "hsnCode": "$product_info.hsn",
            "mrp": "$product_info.mrp",
            "description": "$product_info.description",
            "imageUrl": "$product_info.imageUrl",
            "baseUnit": "$product_info.baseUnit",
            "productDetails": "$product_info",
            "categoryDetails": "$category_info",
            "subcategoryDetails": "$subcategory_info"
        }
    })

    cursor = db["warehouse_products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        
        # Safely parse nested ObjectIds
        if prod.get("productDetails") and "_id" in prod["productDetails"]:
            prod["productDetails"]["id"] = str(prod["productDetails"].pop("_id"))
        if prod.get("categoryDetails") and "_id" in prod["categoryDetails"]:
            prod["categoryDetails"]["id"] = str(prod["categoryDetails"].pop("_id"))
        if prod.get("subcategoryDetails") and "_id" in prod["subcategoryDetails"]:
            prod["subcategoryDetails"]["id"] = str(prod["subcategoryDetails"].pop("_id"))
            
        products.append(prod)
    return products

async def get_mobile_product_details(warehouse_id: str, product_id: str) -> Optional[dict]:
    db = get_db()
    
    try:
        # We will match either the warehouse_product _id OR the global productId
        obj_id = ObjectId(product_id) if len(product_id) == 24 else None
        product_id_query = {"$or": [{"productId": product_id}, {"_id": obj_id}]} if obj_id else {"productId": product_id}
    except:
        product_id_query = {"productId": product_id}

    match_query = {
        "warehouseId": warehouse_id,
        "status": "Active",
        **product_id_query
    }
    
    pipeline = [
        {"$match": match_query},
        {"$addFields": {"productObjectId": {"$toObjectId": "$productId"}}},
        {
            "$lookup": {
                "from": "products",
                "localField": "productObjectId",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {"$match": {"product_info.status": "Active"}},
        {
            "$addFields": {
                "categoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.categoryId", ""]}, {"$ne": ["$product_info.categoryId", None]}]},
                        {"$toObjectId": "$product_info.categoryId"},
                        None
                    ]
                },
                "subcategoryObjectId": {
                    "$cond": [
                        {"$and": [{"$ne": ["$product_info.subcategoryId", ""]}, {"$ne": ["$product_info.subcategoryId", None]}]},
                        {"$toObjectId": "$product_info.subcategoryId"},
                        None
                    ]
                }
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "categoryObjectId",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": "subcategories",
                "localField": "subcategoryObjectId",
                "foreignField": "_id",
                "as": "subcategory_info"
            }
        },
        {"$unwind": {"path": "$subcategory_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 1,
                "productId": 1,
                "availableStock": 1,
                "status": 1,
                "basePrice": {
                    "$cond": [
                        {"$and": [{"$ne": ["$basePrice", None]}, {"$gt": ["$basePrice", 0]}]},
                        "$basePrice", 
                        {"$toDouble": "$product_info.basePrice"}
                    ]
                },
                "name": "$product_info.name",
                "category": "$category_info.name",
                "categoryId": "$product_info.categoryId",
                "subcategoryId": "$product_info.subcategoryId",
                "hsnCode": "$product_info.hsn",
                "mrp": "$product_info.mrp",
                "description": "$product_info.description",
                "imageUrl": "$product_info.imageUrl",
                "baseUnit": "$product_info.baseUnit",
                "productDetails": "$product_info",
                "categoryDetails": "$category_info",
                "subcategoryDetails": "$subcategory_info"
            }
        }
    ]

    cursor = db["warehouse_products"].aggregate(pipeline)
    products = []
    async for prod in cursor:
        prod["id"] = str(prod.pop("_id"))
        
        # Safely parse nested ObjectIds
        if prod.get("productDetails") and "_id" in prod["productDetails"]:
            prod["productDetails"]["id"] = str(prod["productDetails"].pop("_id"))
        if prod.get("categoryDetails") and "_id" in prod["categoryDetails"]:
            prod["categoryDetails"]["id"] = str(prod["categoryDetails"].pop("_id"))
        if prod.get("subcategoryDetails") and "_id" in prod["subcategoryDetails"]:
            prod["subcategoryDetails"]["id"] = str(prod["subcategoryDetails"].pop("_id"))
            
        products.append(prod)
        
    return products[0] if products else None

async def get_mobile_home(warehouse_id: str) -> dict:
    db = get_db()
    
    # 1. Fetch Categories
    categories_cursor = db["categories"].find().limit(10)
    categories = []
    async for cat in categories_cursor:
        cat["id"] = str(cat.pop("_id"))
        # Using a dummy image if none exists
        cat["imageUrl"] = cat.get("name") # Using name as fallback, but typically should have an imageUrl field in categories.
        categories.append(cat)
        
    # 2. Fetch Dummy Banners
    banners = [
        {
            "id": "banner_1",
            "title": "50% OFF On Fresh Vegetables",
            "imageUrl": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80",
            "actionUrl": "/category/vegetables"
        }
    ]
    
    # 3. Fetch Quick Orders (Top Products from Warehouse)
    # We'll just fetch the first 10 active products in the warehouse
    quick_orders = await get_mobile_products(warehouse_id)
    # limit in-memory for simplicity
    quick_orders = quick_orders[:10]
    
    return {
        "banners": banners,
        "categories": categories,
        "quickOrders": quick_orders
    }

async def get_mobile_categories() -> List[dict]:
    db = get_db()
    
    # Aggregation to fetch categories and their respective subcategories
    pipeline = [
        {"$match": {"status": "Active"}}, # Add match if you only want active categories
        {
            "$addFields": {
                "categoryIdString": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "subcategories",
                "localField": "categoryIdString",
                "foreignField": "categoryId",
                "as": "subcategories"
            }
        },
        {
            "$project": {
                "categoryIdString": 0 # Remove temporary field
            }
        }
    ]
    
    cursor = db["categories"].aggregate(pipeline)
    categories = []
    async for cat in cursor:
        cat["id"] = str(cat.pop("_id"))
        
        # Clean up subcategory ObjectIds
        formatted_subs = []
        for sub in cat.get("subcategories", []):
            if "_id" in sub:
                sub["id"] = str(sub.pop("_id"))
            formatted_subs.append(sub)
        cat["subcategories"] = formatted_subs
        
        categories.append(cat)
        
    return categories

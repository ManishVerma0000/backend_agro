from typing import List, Optional
from bson import ObjectId
from app.db.session import get_db
import os
from app.utils.gmaps import get_road_distance

async def get_mobile_products(warehouse_id: str, category_id: Optional[str] = None, subcategory_id: Optional[str] = None, search: Optional[str] = None) -> List[dict]:
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

    # Optional Search Filter
    if search:
        pipeline.append({"$match": {"product_info.name": {"$regex": search, "$options": "i"}}})

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

async def get_nearest_warehouse(lat: float, lon: float) -> Optional[dict]:
    db = get_db()
    api_key = os.getenv("GOOGLE_MAP_KEY")
    
    # Use MongoDB $geoNear as an initial fast filter
    # Straight-line distance is always less than or equal to road distance.
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lon, lat]},
                "distanceField": "distance", # Straight-line distance in meters
                "spherical": True,
                "query": {"status": "Active"},
                "maxDistance": 100000 # Strictly 100km straight-line limit
            }
        },
        {"$limit": 1}
    ]
    
    cursor = db["warehouses"].aggregate(pipeline)
    warehouse = None
    async for w in cursor:
        warehouse = w
        break
        
    if not warehouse:
        return None
        
    # If we have a Google Maps key, calculate accurate road distance
    if api_key:
        dest_lon, dest_lat = warehouse["location_geo"]["coordinates"]
        road_info = await get_road_distance(lat, lon, dest_lat, dest_lon, api_key)
        
        if road_info:
            road_distance = road_info["distance_meters"]
            # Enforce 100km ROAD distance limit
            if road_distance > 100000:
                return None
            
            warehouse["distance"] = road_distance
            warehouse["distance_text"] = road_info["distance_text"]
            warehouse["duration_text"] = road_info["duration_text"]
            warehouse["distance_km"] = round(road_distance / 1000, 2)
        else:
            # Fallback to straight-line
            warehouse["distance_km"] = round(warehouse["distance"] / 1000, 2)
    else:
        warehouse["distance_km"] = round(warehouse["distance"] / 1000, 2)
        
    warehouse["id"] = str(warehouse.pop("_id"))
    return warehouse

async def get_today_price_list(warehouse_id: str, customer_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    
    product_ids = []
    
    # 1. Try to get products from the last order if customer_id is provided
    if customer_id and customer_id != "undefined":
        last_order = await db["mobile_orders"].find_one(
            {"customerId": customer_id, "warehouseId": warehouse_id},
            sort=[("createdAt", -1)]
        )
        if last_order and "items" in last_order:
            for item in last_order["items"]:
                if "productId" in item:
                    product_ids.append(item["productId"])
    
    # 2. If no products from orders, get most sold items in the warehouse
    if not product_ids:
        pipeline = [
            {"$match": {"warehouseId": warehouse_id}},
            {"$unwind": "$items"},
            {"$group": {"_id": "$items.productId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        cursor = db["mobile_orders"].aggregate(pipeline)
        async for doc in cursor:
            product_ids.append(doc["_id"])
            
    # 3. Fallback: If still no products, just get top products from warehouse_products
    if not product_ids:
        cursor = db["warehouse_products"].find({"warehouseId": warehouse_id, "status": "Active"}).limit(10)
        async for wp in cursor:
            product_ids.append(wp["productId"])
            
    # Deduplicate product IDs while preserving order
    unique_product_ids = []
    seen = set()
    for pid in product_ids:
        if pid not in seen:
            unique_product_ids.append(pid)
            seen.add(pid)
    unique_product_ids = unique_product_ids[:10]
            
    # 4. Fetch full details for these product IDs
    # Since we have get_mobile_products, we can adapt it or just call it and filter
    # But for better performance, we'll fetch them individually for now or use a batch approach if possible.
    results = []
    for pid in unique_product_ids:
        p_details = await get_mobile_product_details(warehouse_id, pid)
        if p_details:
            results.append(p_details)
            
    return results

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from dotenv import load_dotenv
import random;
import os
load_dotenv()

class Database:
    client: AsyncIOMotorClient = None

db = Database()

def get_db():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))

async def close_mongo_connection():
    if db.client:
        db.client.close()

from motor.motor_asyncio import AsyncIOMotorClient
from api.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.DATABASE_NAME]
    print("Connected to MongoDB.")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("MongoDB connection closed.")

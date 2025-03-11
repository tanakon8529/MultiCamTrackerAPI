from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """Create database connection."""
    logger.info("Connecting to MongoDB...")
    
    # Connection URI
    if settings.MONGO_USER and settings.MONGO_PASSWORD:
        uri = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}"
    else:
        uri = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}"
    
    # Connect to MongoDB
    db.client = AsyncIOMotorClient(uri)
    
    # Verify connection
    try:
        # The ping command is lightweight and doesn't require auth
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except ConnectionFailure:
        logger.error("MongoDB connection failed")
        raise
    
    # Set database
    db.db = db.client[settings.MONGO_DB]

async def close_mongo_connection():
    """Close database connection."""
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance."""
    return db.db

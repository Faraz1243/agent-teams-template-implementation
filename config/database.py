from .cloud_sql_connector import (
    engine,
    SessionLocal,
    Base,
    get_db,
    db_connector,
    DatabaseConnectionError
)

__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'db_connector',
    'DatabaseConnectionError'
]

# app/config/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import certifi
from .logging import logger
from .config import settings

async def connect_to_mongodb():
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_DATABASE_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
            ssl=True
        )
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logger.error(f"Could not connect to MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        raise
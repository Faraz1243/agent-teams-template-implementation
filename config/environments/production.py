# config/environments/production.py
from .base import BaseEnvironmentConfig, DatabaseConfig, MongoConfig

class ProductionConfig(BaseEnvironmentConfig):
    DATABASE: DatabaseConfig = DatabaseConfig(
        POOL_SIZE=10,
        MAX_OVERFLOW=20,
        POOL_TIMEOUT=60,
        POOL_RECYCLE=1800  # 30 minutes
    )
    MONGO: MongoConfig = MongoConfig(
        MIN_POOL_SIZE=10,
        MAX_POOL_SIZE=50,
        MAX_IDLE_TIME_MS=30000
    )
    LOG_LEVEL: str = "INFO"
    ENABLE_SWAGGER: bool = True
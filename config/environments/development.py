# config/environments/development.py
from .base import BaseEnvironmentConfig, DatabaseConfig, MongoConfig

class DevelopmentConfig(BaseEnvironmentConfig):
    DATABASE: DatabaseConfig = DatabaseConfig(
        POOL_SIZE=2,
        MAX_OVERFLOW=5,
        POOL_TIMEOUT=30
    )
    MONGO: MongoConfig = MongoConfig(
        MIN_POOL_SIZE=1,
        MAX_POOL_SIZE=5
    )
    LOG_LEVEL: str = "DEBUG"
    ENABLE_SWAGGER: bool = True

# app/config/environments/base.py
from typing import Dict, Any
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    POOL_PRE_PING: bool = True

class MongoConfig(BaseModel):
    MIN_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 10
    MAX_IDLE_TIME_MS: int = 50000
    RETRY_WRITES: bool = True

class BaseEnvironmentConfig(BaseModel):
    DATABASE: DatabaseConfig = DatabaseConfig()
    MONGO: MongoConfig = MongoConfig()
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    REQUEST_TIMEOUT: int = 60
    ENABLE_SWAGGER: bool = True
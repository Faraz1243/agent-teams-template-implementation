from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .config import settings
from .logging import logger as app_logger


class DatabaseConnectionError(Exception):
    pass


class CloudSQLConnector:
    def __init__(
        self,
        instance_connection_name: str,
        db_user: str,
        db_pass: str,
        db_name: str
    ):
        self.instance_connection_name = instance_connection_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self._engine = None
        self._SessionLocal = None

        # Create async SQLAlchemy engine
        self._create_engine()

    def _create_engine(self):
        """Create Async SQLAlchemy engine based on environment"""
        try:
            if settings.ENVIRONMENT == "production":
                db_url = (
                    f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
                    f"@/{self.db_name}?host=/cloudsql/{self.instance_connection_name}"
                )
            else:
                db_url = (
                    f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
                    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{self.db_name}"
                )

            app_logger.info(f"Creating Async SQL Engine for environment: {settings.ENVIRONMENT}")

            # Create async engine
            self._engine = create_async_engine(
                db_url,
                pool_size=3,
                max_overflow=1,
                pool_timeout=30,
                pool_pre_ping=True,
                echo=False,
            )

        except Exception as e:
            app_logger.error(f"Failed to create Async SQL Engine: {str(e)}")
            raise DatabaseConnectionError(f"Failed to create Async SQL Engine: {str(e)}")

    @property
    def engine(self):
        """Get SQLAlchemy async engine"""
        if self._engine is None:
            self._create_engine()
        return self._engine

    @property
    def SessionLocal(self):
        """Get Async SQLAlchemy session maker"""
        if self._SessionLocal is None:
            self._SessionLocal = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._SessionLocal

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope around a series of operations (async)."""
        async with self.SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                app_logger.error(f"Database async session error: {str(e)}")
                raise

    async def dispose(self):
        """Dispose of the async engine"""
        if self._engine:
            await self._engine.dispose()
            app_logger.info("Disposed async SQL connection")


Base = declarative_base()


# Initialize the connector
try:
    app_logger.info("Initializing Async Cloud SQL connection...")
    db_connector = CloudSQLConnector(
        instance_connection_name=settings.POSTGRES_INSTANCE_CONNECTION_NAME,
        db_user=settings.POSTGRES_USER,
        db_pass=settings.POSTGRES_PASSWORD,
        db_name=settings.POSTGRES_DB
    )

    engine = db_connector.engine
    SessionLocal = db_connector.SessionLocal
    get_db = db_connector.get_db

except Exception as e:
    app_logger.error(f"Failed to initialize Async Cloud SQL connector: {str(e)}")
    raise


# ✅ FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    async with SessionLocal() as session:
        yield session
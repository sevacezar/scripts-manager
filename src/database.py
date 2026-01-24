"""Database configuration and session management."""

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)

# Base class for models
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable foreign key constraints for SQLite.
    SQLite disables foreign keys by default for backwards compatibility.
    """
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database - create all tables.
    Should be called on application startup in development.
    """
    async with engine.begin() as conn:
        # Enable foreign keys for SQLite
        if "sqlite" in settings.database_url:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
        # Enable foreign keys again after table creation (for safety)
        if "sqlite" in settings.database_url:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
    logger.info("Database initialized", database_url=settings.database_url)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


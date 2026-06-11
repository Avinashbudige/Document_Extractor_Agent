"""Database session management and dependency injection for FastAPI."""

from typing import Generator
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
import logging

from src.models.config import settings

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=pool.QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging in development
)


# Event listener for connection pool logging
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when a new database connection is established."""
    logger.debug("Database connection established")


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool."""
    logger.debug("Connection checked out from pool")


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    This function creates a new SQLAlchemy session for each request,
    yields it to the route handler, and ensures it's properly closed
    after the request is complete.
    
    Usage in FastAPI routes:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from src.storage.database import get_db
        
        @router.get("/documents/{id}")
        def get_document(id: str, db: Session = Depends(get_db)):
            document = db.query(Document).filter(Document.id == id).first()
            return document
        ```
    """
    db = SessionLocal()
    try:
        logger.debug("Creating new database session")
        yield db
    except Exception as e:
        logger.error(f"Error during database session: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function should be called during application startup
    to ensure all tables are created. In production, use Alembic
    migrations instead of this function.
    
    Note:
        This is primarily for development and testing. Production
        deployments should use Alembic migrations.
    """
    from src.storage.models import Base
    
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")


def get_db_health() -> bool:
    """
    Check database connectivity for health checks.
    
    Returns:
        bool: True if database is reachable, False otherwise
        
    Example:
        ```python
        @router.get("/health")
        def health_check():
            db_healthy = get_db_health()
            return {"database": "healthy" if db_healthy else "unhealthy"}
        ```
    """
    try:
        db = SessionLocal()
        try:
            # Execute a simple query to verify connectivity
            db.execute("SELECT 1")
            logger.debug("Database health check passed")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def close_db_connections() -> None:
    """
    Close all database connections and dispose of the connection pool.
    
    This function should be called during application shutdown
    to ensure all connections are properly closed.
    
    Example:
        ```python
        @app.on_event("shutdown")
        async def shutdown_event():
            close_db_connections()
        ```
    """
    logger.info("Closing database connections")
    engine.dispose()
    logger.info("Database connections closed")

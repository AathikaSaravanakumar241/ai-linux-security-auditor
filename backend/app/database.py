"""
SQLAlchemy database engine, session factory, and initialization.

Architecture:
    - Engine uses connection pooling (pool_size=5, max_overflow=10) to prevent
      connection exhaustion under concurrent requests.
    - pool_pre_ping=True detects stale connections before handing them out.
    - get_db() is a FastAPI dependency that yields a session and guarantees
      cleanup (commit on success, rollback on exception).
    - init_db() creates all ORM tables on application startup.

Cloud Deployment Note:
    For production, consider using PgBouncer as an external connection pooler
    and switching to NullPool in SQLAlchemy. The DATABASE_URL can be swapped
    to a managed PostgreSQL instance (Cloud SQL, RDS) via environment variable.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        echo=False,  # Set to True for SQL query debugging
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session.

    Yields a SQLAlchemy Session, commits on success, rolls back on
    exception, and always closes the session.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Create all ORM tables if they do not exist.

    Called once during FastAPI startup. Import models here to ensure
    they are registered with the Base metadata before create_all().
    """
    import app.models  # noqa: F401 — registers models with Base.metadata

    logger.info("Creating database tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")

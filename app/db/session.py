"""
Database session and connection management for AI Teacher.
Supports PostgreSQL (via DATABASE_URL) and persistent SQLite (sqlite:///data/ai_teacher.db).
"""

from __future__ import annotations
import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger("DatabaseSession")

Base = declarative_base()

_ENGINE = None
_SESSION_FACTORY = None


def get_database_url() -> str:
    """Returns the configured database URL or defaults to SQLite."""
    url = os.getenv("DATABASE_URL")
    if url:
        # Standardize postgres:// to postgresql:// for SQLAlchemy
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    # Default to local persistent SQLite
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "ai_teacher.db")
    return f"sqlite:///{db_path}"


def get_engine():
    """Initializes and returns the singleton SQLAlchemy engine."""
    global _ENGINE
    if _ENGINE is None:
        db_url = get_database_url()
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        
        try:
            _ENGINE = create_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True,
                echo=False,
            )
            logger.info(f"Initialized database engine for: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    return _ENGINE


def get_session_factory():
    """Returns the singleton sessionmaker."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SESSION_FACTORY


def get_db_session() -> Generator[Session, None, None]:
    """Yields a database session with automatic cleanup and rollback on exception."""
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_db():
    """Initializes database tables defined in models."""
    engine = get_engine()
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized and verified.")

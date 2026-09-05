"""
Database session and connection management for AI Teacher.
Supports PostgreSQL (via DATABASE_URL) and persistent SQLite (sqlite:///data/ai_teacher.db).
"""

from __future__ import annotations
import os
import logging
from typing import Generator
from contextlib import contextmanager
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
    """Initializes and returns the singleton SQLAlchemy engine with automatic SQLite fallback."""
    global _ENGINE
    if _ENGINE is None:
        db_url = get_database_url()
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        
        try:
            engine = create_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True,
                echo=False,
            )
            # Test connection immediately
            with engine.connect() as conn:
                pass
            _ENGINE = engine
            logger.info(f"Initialized database engine for: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        except Exception as e:
            if not db_url.startswith("sqlite"):
                logger.warning(
                    f"Failed to connect to primary database ({e}). "
                    f"Falling back seamlessly to local SQLite database."
                )
                data_dir = os.path.join(os.getcwd(), "data")
                os.makedirs(data_dir, exist_ok=True)
                sqlite_url = f"sqlite:///{os.path.join(data_dir, 'ai_teacher.db')}"
                _ENGINE = create_engine(
                    sqlite_url,
                    connect_args={"check_same_thread": False},
                    pool_pre_ping=True,
                    echo=False,
                )
            else:
                raise
    return _ENGINE


def get_session_factory():
    """Returns the singleton sessionmaker."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SESSION_FACTORY


@contextmanager
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
    """Initializes database tables defined in models and applies safe column migrations."""
    engine = get_engine()
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safe schema migration for newly added columns
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "uploaded_documents" in inspector.get_table_names():
            existing_cols = {c["name"] for c in inspector.get_columns("uploaded_documents")}
            new_columns = [
                ("student_id", "VARCHAR(64) DEFAULT 'default_student' NOT NULL"),
                ("course", "VARCHAR(128)"),
                ("chapter", "VARCHAR(255)"),
                ("processing_state", "VARCHAR(32) DEFAULT 'READY' NOT NULL"),
                ("concepts_json", "TEXT DEFAULT '[]' NOT NULL"),
                ("understanding_json", "TEXT"),
            ]
            with engine.connect() as conn:
                for col_name, col_def in new_columns:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE uploaded_documents ADD COLUMN {col_name} {col_def}"))
                conn.commit()

        if "learner_profiles" in inspector.get_table_names():
            existing_cols = {c["name"] for c in inspector.get_columns("learner_profiles")}
            learner_columns = [
                ("college_grade", "VARCHAR(128)"),
                ("college", "VARCHAR(255)"),
                ("department", "VARCHAR(255)"),
                ("degree", "VARCHAR(128)"),
                ("year", "INTEGER DEFAULT 1"),
                ("semester", "INTEGER DEFAULT 1"),
                ("available_study_hours", "FLOAT DEFAULT 10.0"),
                ("target_exam", "VARCHAR(128)"),
                ("exam_date", "VARCHAR(64)"),
                ("exam_dates_json", "TEXT DEFAULT '{}' NOT NULL"),
                ("courses_json", "TEXT DEFAULT '[]' NOT NULL"),
                ("target_score", "VARCHAR(32)"),
                ("learning_speed", "VARCHAR(32) DEFAULT 'moderate' NOT NULL"),
                ("preferred_teaching_style", "VARCHAR(64) DEFAULT 'FORMAL_RIGOROUS' NOT NULL"),
                ("study_history_json", "TEXT DEFAULT '{}' NOT NULL"),
            ]
            with engine.connect() as conn:
                for col_name, col_def in learner_columns:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE learner_profiles ADD COLUMN {col_name} {col_def}"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Schema migration warning: {e}")

    logger.info("Database schema initialized and verified.")



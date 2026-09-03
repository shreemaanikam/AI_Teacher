"""
Database and Persistence Package for AI Teacher.
"""

from app.db.session import Base, get_db_session, get_engine, init_db
from app.db.models import (
    TeachingSessionModel,
    TeachingStateEventModel,
    QuestionModel,
    ResponseModel,
    MasteryRecordModel,
    LearningReportModel,
    MediaSegmentModel,
    TeachingTraceModel,
)
from app.db.repository import (
    TeachingRepository,
    SQLAlchemyTeachingRepository,
    MemoryTeachingRepository,
    get_teaching_repository,
)

__all__ = [
    "Base",
    "get_db_session",
    "get_engine",
    "init_db",
    "TeachingSessionModel",
    "TeachingStateEventModel",
    "QuestionModel",
    "ResponseModel",
    "MasteryRecordModel",
    "LearningReportModel",
    "MediaSegmentModel",
    "TeachingTraceModel",
    "TeachingRepository",
    "SQLAlchemyTeachingRepository",
    "MemoryTeachingRepository",
    "get_teaching_repository",
]

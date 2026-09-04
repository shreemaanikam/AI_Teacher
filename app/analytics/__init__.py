"""
Module 10: Learning Analytics & Recommendation Engine package.
"""

from app.analytics.models import (
    LearningEvent,
    LearningEventType,
    MasteryTrend,
    ConceptAnalytics,
    MisconceptionAnalytics,
    RevisionRecommendation,
    LearningPath,
    LearningReportSummary,
)
from app.analytics.event_logger import LearningEventLogger, get_event_logger
from app.analytics.analytics_engine import LearningAnalyticsEngine
from app.analytics.recommendations import RevisionRecommendationEngine
from app.analytics.learning_path import LearningPathEngine

__all__ = [
    "LearningEvent",
    "LearningEventType",
    "MasteryTrend",
    "ConceptAnalytics",
    "MisconceptionAnalytics",
    "RevisionRecommendation",
    "LearningPath",
    "LearningReportSummary",
    "LearningEventLogger",
    "get_event_logger",
    "LearningAnalyticsEngine",
    "RevisionRecommendationEngine",
    "LearningPathEngine",
]

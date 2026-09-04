"""
Data models and schemas for Module 10: Learning Analytics & Recommendation Engine.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.harness.session import TeachingStrategy


class LearningEventType(str, Enum):
    LESSON_STARTED = "LESSON_STARTED"
    CONCEPT_INTRODUCED = "CONCEPT_INTRODUCED"
    QUESTION_ANSWERED = "QUESTION_ANSWERED"
    MISCONCEPTION_DETECTED = "MISCONCEPTION_DETECTED"
    MISCONCEPTION_RESOLVED = "MISCONCEPTION_RESOLVED"
    CONCEPT_MASTERED = "CONCEPT_MASTERED"
    REVISION_COMPLETED = "REVISION_COMPLETED"
    LESSON_COMPLETED = "LESSON_COMPLETED"


class MasteryTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    NEW = "NEW"


class LearningEvent(BaseModel):
    """Atomic telemetry event recorded during student learning activities."""
    event_id: str = Field(default_factory=lambda: f"levt_{uuid.uuid4().hex[:8]}")
    learner_id: str
    session_id: Optional[str] = None
    concept_id: str
    event_type: LearningEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    score: Optional[float] = None
    difficulty: int = 2
    strategy: Optional[TeachingStrategy] = None
    language: str = "en"
    duration_seconds: float = 0.0
    payload: Dict[str, Any] = Field(default_factory=dict)


class ConceptAnalytics(BaseModel):
    """Aggregated analytical telemetry for a single subject concept."""
    concept: str
    mastery: float
    confidence: float
    total_attempts: int = 0
    correct_attempts: int = 0
    incorrect_attempts: int = 0
    misconceptions: List[str] = Field(default_factory=list)
    last_studied: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trend: MasteryTrend = MasteryTrend.NEW
    recommended_action: str = "Continue standard progression"


class MisconceptionAnalytics(BaseModel):
    """Analytical tracking of a diagnosed cognitive flaw."""
    misconception_type: str
    occurrences: int = 1
    resolved_count: int = 0
    resolution_rate: float = 0.0
    concepts_affected: List[str] = Field(default_factory=list)
    effective_remediations: List[str] = Field(default_factory=list)
    status: str = "RESOLVED"  # RESOLVED, NEEDS_REVISION, ACTIVE


class RevisionRecommendation(BaseModel):
    """Targeted revision recommendation scheduled for a learner."""
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    concept: str
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    reason: str
    recommended_duration_minutes: int = 10
    recommended_strategy: TeachingStrategy = TeachingStrategy.SIMPLE_ANALOGY
    question_count: int = 2


class LearningPath(BaseModel):
    """Personalized curriculum roadmap navigating prerequisite dependency graph."""
    path_id: str = Field(default_factory=lambda: f"lpath_{uuid.uuid4().hex[:8]}")
    learner_id: str
    subject: str = "physics"
    goal: str
    current_topic: str
    completed_topics: List[str] = Field(default_factory=list)
    next_topics: List[str] = Field(default_factory=list)
    blocked_topics: List[str] = Field(default_factory=list)
    recommended_topics: List[str] = Field(default_factory=list)


class LearningReportSummary(BaseModel):
    """Comprehensive analytical report generated upon session completion."""
    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    learner_id: str
    session_id: str
    subject: str
    total_duration_minutes: float
    final_score: float
    concepts_understood: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    misconceptions_detected: List[str] = Field(default_factory=list)
    resolved_misconceptions: List[str] = Field(default_factory=list)
    mastery_changes: Dict[str, float] = Field(default_factory=dict)
    recommended_revisions: List[RevisionRecommendation] = Field(default_factory=list)
    recommended_next_topics: List[str] = Field(default_factory=list)
    overall_feedback: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

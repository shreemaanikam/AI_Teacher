"""
SQLAlchemy ORM models for AI Teacher entity registry and persistence.
Maps 1-to-1 with PostgreSQL 16 schema in docs/technical/backend_schema.md.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class TeachingSessionModel(Base):
    """Runtime state and position of a teaching session (E-014)."""
    __tablename__ = "teaching_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    lesson_id = Column(String(64), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    subject = Column(String(64), nullable=False, default="physics")
    current_state = Column(String(32), nullable=False, default="START")
    previous_state = Column(String(32), nullable=True)
    current_concept = Column(String(255), nullable=False)
    current_strategy = Column(String(64), nullable=False, default="DIRECT_EXPLANATION")
    current_difficulty = Column(Integer, nullable=False, default=2)
    language = Column(String(35), nullable=False, default="en")
    consecutive_failures = Column(Integer, nullable=False, default=0)
    consecutive_successes = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    
    # Serialized JSON fields
    concepts_list_json = Column(Text, nullable=False, default="[]")
    concept_mastery_json = Column(Text, nullable=False, default="{}")
    active_misconceptions_json = Column(Text, nullable=False, default="[]")
    resolved_misconceptions_json = Column(Text, nullable=False, default="[]")
    metadata_json = Column(Text, nullable=False, default="{}")

    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_activity_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    events = relationship("TeachingStateEventModel", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("ResponseModel", back_populates="session", cascade="all, delete-orphan")
    traces = relationship("TeachingTraceModel", back_populates="session", cascade="all, delete-orphan")


class TeachingStateEventModel(Base):
    """Audit log of state transitions (E-021)."""
    __tablename__ = "teaching_state_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("teaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(32), nullable=False)
    to_state = Column(String(32), nullable=False)
    trigger_action = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("TeachingSessionModel", back_populates="events")


class QuestionModel(Base):
    """Versioned checkpoint and assessment questions (E-015)."""
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True, index=True)
    lesson_id = Column(String(64), nullable=False, index=True)
    concept = Column(String(255), nullable=False, index=True)
    type = Column(String(32), nullable=False, default="conceptual")
    prompt = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False, default=2)
    language = Column(String(35), nullable=False, default="en")
    is_final = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)

    # Serialized JSON
    options_json = Column(Text, nullable=True)
    rubric_json = Column(Text, nullable=False, default="{}")
    misconception_targets_json = Column(Text, nullable=True)
    prerequisite_concepts_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResponseModel(Base):
    """Learner attempts and evaluation results (E-016)."""
    __tablename__ = "responses"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("teaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(64), ForeignKey("questions.id"), nullable=False, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    student_answer = Column(Text, nullable=False)
    verdict = Column(String(32), nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    misconception_code = Column(String(128), nullable=True)
    misconception_belief = Column(Text, nullable=True)
    deterministic_validation = Column(Boolean, nullable=False, default=False)
    evaluator_reason = Column(Text, nullable=True)
    rubric_matches_json = Column(Text, nullable=True)
    rubric_misses_json = Column(Text, nullable=True)

    submitted_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("TeachingSessionModel", back_populates="responses")


class MasteryRecordModel(Base):
    """Current per-user concept mastery snapshot (E-017)."""
    __tablename__ = "mastery_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False, index=True)
    concept_id = Column(String(255), nullable=False, index=True)
    mastery = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=False, default=0.5)
    evidence_count = Column(Integer, nullable=False, default=1)
    last_response_id = Column(String(64), nullable=True)
    last_practiced_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_user_concept_mastery"),
    )


class LearningReportModel(Base):
    """Final session outcome and recommendations (E-018)."""
    __tablename__ = "learning_reports"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("teaching_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(String(64), nullable=False, index=True)
    lesson_id = Column(String(64), nullable=False, index=True)
    final_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    concept_mastery_json = Column(Text, nullable=False)
    strengths_json = Column(Text, nullable=False)
    resolved_misconceptions_json = Column(Text, nullable=False)
    recommended_topics_json = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class MediaSegmentModel(Base):
    """Generated media segments with script, audio, avatar, and captions (E-013)."""
    __tablename__ = "media_segments"

    id = Column(String(64), primary_key=True, index=True)
    lesson_id = Column(String(64), nullable=False, index=True)
    concept = Column(String(255), nullable=False)
    teaching_strategy = Column(String(64), nullable=False)
    language = Column(String(35), nullable=False)
    duration_seconds = Column(Float, nullable=False)
    status = Column(String(32), nullable=False, default="READY")
    is_fallback = Column(Boolean, nullable=False, default=False)
    video_url = Column(String(512), nullable=True)

    script_json = Column(Text, nullable=False)
    audio_json = Column(Text, nullable=False)
    avatar_json = Column(Text, nullable=False)
    visual_json = Column(Text, nullable=True)
    captions_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TeachingTraceModel(Base):
    """Structured AI Teaching Trace entries for observability and judge auditing."""
    __tablename__ = "teaching_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("teaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    trace_id = Column(String(64), nullable=False, index=True)
    concept = Column(String(255), nullable=False)
    learner_level = Column(String(32), nullable=False)
    from_state = Column(String(32), nullable=False)
    to_state = Column(String(32), nullable=False)
    question_id = Column(String(64), nullable=True)
    student_response = Column(Text, nullable=True)
    evaluation_result = Column(String(32), nullable=True)
    misconception_type = Column(String(128), nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    previous_strategy = Column(String(64), nullable=True)
    new_strategy = Column(String(64), nullable=False)
    visual_strategy = Column(String(64), nullable=False)
    next_action = Column(String(64), nullable=False)
    media_status = Column(String(32), nullable=False, default="READY")
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("TeachingSessionModel", back_populates="traces")

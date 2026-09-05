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


class LearnerProfileModel(Base):
    """Persistent learner profile and cognitive settings."""
    __tablename__ = "learner_profiles"

    id = Column(String(64), primary_key=True, index=True)
    display_name = Column(String(255), nullable=False, default="Learner")
    educational_level = Column(String(32), nullable=False, default="beginner")
    preferred_language = Column(String(35), nullable=False, default="en")
    material_language = Column(String(35), nullable=False, default="en")
    teaching_style = Column(String(64), nullable=False, default="SIMPLE")
    available_time = Column(String(32), nullable=False, default="20_MIN")
    custom_time_minutes = Column(Integer, nullable=False, default=20)
    desired_depth = Column(String(64), nullable=False, default="foundation")
    subject = Column(String(64), nullable=False, default="physics")
    college_grade = Column(String(128), nullable=True)
    college = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    degree = Column(String(128), nullable=True)
    year = Column(Integer, nullable=True, default=1)
    semester = Column(Integer, nullable=True, default=1)
    available_study_hours = Column(Float, nullable=True, default=10.0)
    target_exam = Column(String(128), nullable=True)
    exam_date = Column(String(64), nullable=True)
    exam_dates_json = Column(Text, nullable=False, default="{}")
    courses_json = Column(Text, nullable=False, default="[]")
    target_score = Column(String(32), nullable=True)
    learning_speed = Column(String(32), nullable=False, default="moderate")
    preferred_teaching_style = Column(String(64), nullable=False, default="FORMAL_RIGOROUS")
    knowledge_json = Column(Text, nullable=False, default="{}")
    weak_concepts_json = Column(Text, nullable=False, default="[]")
    strengths_json = Column(Text, nullable=False, default="[]")
    misconceptions_json = Column(Text, nullable=False, default="[]")
    study_history_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class CourseModel(Base):
    """Enrolled collegiate subject/course for a student."""
    __tablename__ = "courses"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    code = Column(String(32), nullable=False)
    name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    semester = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    exam_date = Column(String(64), nullable=True)
    target_score = Column(String(32), nullable=False, default="90%")
    status = Column(String(32), nullable=False, default="ACTIVE")
    units_json = Column(Text, nullable=False, default="[]")
    concepts_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class UploadedDocumentModel(Base):
    """Metadata for uploaded files validated by Module 1 & Module 2."""
    __tablename__ = "uploaded_documents"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), nullable=False, default="default_student", index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(128), nullable=False)
    extension = Column(String(32), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sha256_checksum = Column(String(128), nullable=False)
    detected_language = Column(String(35), nullable=False, default="en")
    detected_title = Column(String(255), nullable=True)
    detected_subject = Column(String(64), nullable=True)
    course = Column(String(128), nullable=True)
    chapter = Column(String(255), nullable=True)
    page_count = Column(Integer, nullable=False, default=1)
    ocr_provider_used = Column(String(64), nullable=False, default="native_extractor")
    processing_state = Column(String(32), nullable=False, default="READY")  # UPLOAD, PARSE, UNDERSTAND, STRUCTURE, INDEX, READY, FAILED
    concepts_json = Column(Text, nullable=False, default="[]")
    structure_json = Column(Text, nullable=True)
    understanding_json = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    """Extracted semantic chunks persisted in PostgreSQL for hybrid RAG."""
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_type = Column(String(32), nullable=False, default="concept")
    chapter = Column(String(255), nullable=True)
    section = Column(String(255), nullable=True)
    concept = Column(String(255), nullable=True, index=True)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    document = relationship("UploadedDocumentModel", back_populates="chunks")


class LearningEventModel(Base):
    """Granular learning telemetry events persisted in PostgreSQL."""
    __tablename__ = "learning_events"

    id = Column(String(64), primary_key=True, index=True)
    learner_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    concept_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    score = Column(Float, nullable=True)
    difficulty = Column(Integer, nullable=False, default=2)
    strategy = Column(String(64), nullable=True)
    language = Column(String(35), nullable=False, default="en")
    duration_seconds = Column(Float, nullable=False, default=0.0)
    payload_json = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TaskModel(Base):
    """Student study tasks and deadlines for Phase 9L."""
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    course_id = Column(String(64), nullable=True, index=True)
    course_name = Column(String(255), nullable=True)
    concept = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    task_type = Column(String(32), nullable=False, default="REVISION")  # REVISION, PRACTICE, ASSIGNMENT, EXAM_PREP
    priority = Column(String(16), nullable=False, default="MEDIUM")  # HIGH, MEDIUM, LOW
    deadline = Column(String(64), nullable=True)  # YYYY-MM-DD
    estimated_duration_minutes = Column(Integer, nullable=False, default=30)
    status = Column(String(32), nullable=False, default="TODO")  # TODO, IN_PROGRESS, COMPLETED, OVERDUE
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ExamPlanModel(Base):
    """Personalized multi-day collegiate exam study plan for Phase 9J & 9K."""
    __tablename__ = "exam_plans"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    course_id = Column(String(64), nullable=False, index=True)
    course_name = Column(String(255), nullable=False)
    exam_date = Column(String(64), nullable=False)
    target_score = Column(String(32), nullable=False, default="90%")
    available_hours_per_day = Column(Float, nullable=False, default=2.0)
    total_days = Column(Integer, nullable=False, default=7)
    schedule_json = Column(Text, nullable=False, default="[]")
    status = Column(String(32), nullable=False, default="ACTIVE")  # ACTIVE, REPLANNED, COMPLETED
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class AssignmentModel(Base):
    """Curriculum-grounded adaptive assignment for Phase 9M."""
    __tablename__ = "assignments"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    course_id = Column(String(64), nullable=True, index=True)
    course_name = Column(String(255), nullable=False)
    concept = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    assignment_type = Column(String(32), nullable=False, default="PRACTICE_SET")
    difficulty = Column(String(32), nullable=False, default="INTERMEDIATE")
    questions_json = Column(Text, nullable=False, default="[]")
    deadline = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="ASSIGNED")  # ASSIGNED, SUBMITTED, GRADED
    score = Column(Float, nullable=True)
    feedback_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class SubmissionModel(Base):
    """Student assignment submission and pedagogical evaluation for Phase 9N."""
    __tablename__ = "submissions"

    id = Column(String(64), primary_key=True, index=True)
    assignment_id = Column(String(64), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    answers_json = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    verdict = Column(String(32), nullable=False)
    feedback = Column(Text, nullable=False)
    misconceptions_json = Column(Text, nullable=False, default="[]")
    submitted_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)



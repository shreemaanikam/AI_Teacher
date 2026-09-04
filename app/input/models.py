"""
Data models and schemas for Module 1: Student & Input Intelligence.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class LearnerLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TimeBudget(str, Enum):
    FIVE_MIN = "5_MIN"
    TWENTY_MIN = "20_MIN"
    SIXTY_MIN = "60_MIN"
    CUSTOM = "CUSTOM"


class TeachingStyle(str, Enum):
    SIMPLE = "SIMPLE"
    DETAILED = "DETAILED"
    EXAM_FOCUSED = "EXAM_FOCUSED"
    PRACTICAL = "PRACTICAL"
    SOCRATIC = "SOCRATIC"


class QuestionPreferenceType(str, Enum):
    MCQ = "MCQ"
    CONCEPTUAL = "CONCEPTUAL"
    SHORT_ANSWER = "SHORT_ANSWER"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    APPLICATION = "APPLICATION"


class LearnerProfile(BaseModel):
    """Structured learner profile and educational preferences."""
    learner_id: str = Field(default_factory=lambda: f"learner_{uuid.uuid4().hex[:8]}")
    display_name: str = "Learner"
    educational_level: LearnerLevel = LearnerLevel.BEGINNER
    existing_knowledge: Dict[str, float] = Field(default_factory=dict)
    learning_objective: str = "Master core conceptual principles"
    preferred_language: str = "en"
    material_language: str = "en"
    teaching_style: TeachingStyle = TeachingStyle.SIMPLE
    available_time: TimeBudget = TimeBudget.TWENTY_MIN
    custom_time_minutes: int = 20
    desired_depth: str = "foundation"
    subject: str = "physics"
    exam_target: Optional[str] = None
    preferred_question_types: List[QuestionPreferenceType] = Field(
        default_factory=lambda: [QuestionPreferenceType.CONCEPTUAL, QuestionPreferenceType.MCQ]
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UploadedDocumentMetadata(BaseModel):
    """Metadata for uploaded files validated by Module 1."""
    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    original_filename: str
    sanitized_storage_filename: str
    file_path: str
    mime_type: str
    extension: str
    file_size_bytes: int
    sha256_checksum: str
    detected_language: str = "en"
    detected_title: Optional[str] = None
    detected_subject: Optional[str] = None
    page_or_slide_count: int = 1
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TopicDetectionResult(BaseModel):
    """Result of automated topic and concept detection from source text or documents."""
    detected_topic: str
    detected_subject: str
    detected_chapter: Optional[str] = None
    candidate_concepts: List[str] = Field(default_factory=list)
    confidence: float = 0.9
    source: str = "document_heuristic"


class TeachingRequest(BaseModel):
    """
    Normalized, validated teaching request produced by Module 1.
    Consumed directly by Module 2 (RAG), Module 3 (Learner), Module 4 (Planner), and Module 5 (Harness).
    """
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    learner_id: str
    source_type: str  # "direct_topic" | "uploaded_document" | "mixed"
    source_reference: Optional[str] = None  # document_id or None
    topic: str
    subject: str = "physics"
    chapter: Optional[str] = None
    concepts_list: List[str] = Field(default_factory=list)
    requested_language: str = "en"
    material_language: str = "en"
    learner_level: LearnerLevel = LearnerLevel.BEGINNER
    available_time: TimeBudget = TimeBudget.TWENTY_MIN
    time_minutes: int = 20
    learning_objective: str = "Understand core principles and applications"
    teaching_style: TeachingStyle = TeachingStyle.SIMPLE
    desired_depth: str = "foundation"
    requested_question_types: List[QuestionPreferenceType] = Field(
        default_factory=lambda: [QuestionPreferenceType.CONCEPTUAL, QuestionPreferenceType.MCQ]
    )
    learner_profile: Optional[LearnerProfile] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

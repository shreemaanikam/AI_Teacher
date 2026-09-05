"""
Data models and contracts for Module 3: Learner Cognitive Model.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.harness.session import TeachingStrategy, DifficultyLevel


class KnowledgeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    INTRODUCED = "INTRODUCED"
    LEARNING = "LEARNING"
    STRUGGLING = "STRUGGLING"
    MISCONCEPTION = "MISCONCEPTION"
    DEVELOPING = "DEVELOPING"
    MASTERED = "MASTERED"


class MisconceptionMemory(BaseModel):
    """Persistent tracking of a diagnosed student misconception across sessions."""
    memory_id: str = Field(default_factory=lambda: f"misc_mem_{uuid.uuid4().hex[:8]}")
    misconception_type: str
    concept: str
    first_detected: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_detected: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    frequency: int = 1
    severity: str = "high"
    resolved: bool = False
    remediation_used: Optional[str] = None
    recovery_evidence: Optional[str] = None


class StrategyEffectivenessRecord(BaseModel):
    """Tracks which pedagogical intervention successfully improved mastery for a student."""
    record_id: str = Field(default_factory=lambda: f"strat_{uuid.uuid4().hex[:8]}")
    concept: str
    strategy: TeachingStrategy
    before_mastery: float
    after_mastery: float
    is_effective: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnswerAttemptLog(BaseModel):
    """Record of a question answer attempt by the student."""
    attempt_id: str = Field(default_factory=lambda: f"att_{uuid.uuid4().hex[:8]}")
    question_id: str
    concept: str
    difficulty: int
    student_answer: str
    is_correct: bool
    score: float
    misconception_diagnosed: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnerCognitiveState(BaseModel):
    """
    Complete persistent cognitive profile of a student.
    Guaranteed 100% language-independent.
    """
    learner_id: str
    display_name: str = "Student"
    language: str = "en"
    educational_level: str = "beginner"
    learning_objective: str = "Understand foundational principles"
    preferred_style: str = "SIMPLE"
    available_time_minutes: int = 20
    current_concept: Optional[str] = None
    current_mastery: float = 0.0
    concept_mastery: Dict[str, float] = Field(default_factory=dict)
    knowledge_states: Dict[str, KnowledgeState] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    misconceptions: List[MisconceptionMemory] = Field(default_factory=list)
    strategy_history: List[StrategyEffectivenessRecord] = Field(default_factory=list)
    recent_answers: List[AnswerAttemptLog] = Field(default_factory=list)
    recommended_next_topics: List[str] = Field(default_factory=list)
    confidence: float = 0.80
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MasteryUpdateResult(BaseModel):
    concept: str
    previous_mastery: float
    new_mastery: float
    knowledge_state: KnowledgeState
    delta: float
    reason: str
    confidence: float


class StudentProfile(BaseModel):
    """
    Real student identity model for college students.
    Supports degree, department, study goals, exam schedules, and personalized learning style.
    """
    student_id: str = Field(default_factory=lambda: f"std_{uuid.uuid4().hex[:8]}")
    name: str = "College Student"
    college: str = "College of Engineering"
    department: str = "Computer Science and Engineering"
    degree: str = "B.Tech"
    year: int = 2
    semester: int = 4
    preferred_language: str = "en"
    learning_style: str = "VISUAL_AND_ANALOGIES"  # FORMAL_RIGOROUS, VISUAL_AND_ANALOGIES, PRACTICAL_APPLICATION, SIMPLE
    target_score: str = "90%"
    available_study_hours: float = 15.0
    exam_dates: Dict[str, str] = Field(default_factory=dict)
    enrolled_courses: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CourseUnit(BaseModel):
    unit_id: str = Field(default_factory=lambda: f"unit_{uuid.uuid4().hex[:6]}")
    title: str
    order: int = 1
    concepts: List[str] = Field(default_factory=list)
    completed: bool = False


class CourseDetail(BaseModel):
    """
    Collegiate course/subject structure belonging to a student.
    Supports units, concepts, materials, assignments, and exam deadlines.
    """
    course_id: str = Field(default_factory=lambda: f"crs_{uuid.uuid4().hex[:8]}")
    student_id: str
    code: str
    name: str
    department: Optional[str] = None
    semester: int = 1
    description: Optional[str] = None
    exam_date: Optional[str] = None
    target_score: str = "90%"
    status: str = "ACTIVE"
    units: List[CourseUnit] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



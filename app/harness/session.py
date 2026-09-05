"""
Teaching Session Models and State Schema for Module 5 (Teaching Harness).
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SessionState(str, Enum):
    START = "START"
    UNDERSTAND = "UNDERSTAND"
    PLAN = "PLAN"
    TEACH = "TEACH"
    QUESTION = "QUESTION"
    EVALUATE = "EVALUATE"
    ADAPT = "ADAPT"
    REEXPLAIN = "REEXPLAIN"
    REQUESTION = "REQUESTION"
    ASSESSMENT = "ASSESSMENT"
    REPORT = "REPORT"
    COMPLETE = "COMPLETE"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class TeachingStrategy(str, Enum):
    DIRECT_EXPLANATION = "DIRECT_EXPLANATION"
    SIMPLE_ANALOGY = "SIMPLE_ANALOGY"
    STEP_BY_STEP = "STEP_BY_STEP"
    EXAMPLE_FIRST = "EXAMPLE_FIRST"
    VISUAL_EXPLANATION = "VISUAL_EXPLANATION"
    CONTRASTIVE_EXPLANATION = "CONTRASTIVE_EXPLANATION"
    PREREQUISITE_REVIEW = "PREREQUISITE_REVIEW"
    SOCRATIC_QUESTIONING = "SOCRATIC_QUESTIONING"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    SUMMARY_RECAP = "SUMMARY_RECAP"


class ActionType(str, Enum):
    START_LESSON = "START_LESSON"
    UNDERSTAND_LEARNER = "UNDERSTAND_LEARNER"
    GENERATE_PLAN = "GENERATE_PLAN"
    DELIVER_EXPLANATION = "DELIVER_EXPLANATION"
    ASK_QUESTION = "ASK_QUESTION"
    EVALUATE_RESPONSE = "EVALUATE_RESPONSE"
    ADAPT_STRATEGY = "ADAPT_STRATEGY"
    REEXPLAIN_CONCEPT = "REEXPLAIN_CONCEPT"
    ASK_RECHECK_QUESTION = "ASK_RECHECK_QUESTION"
    RUN_ASSESSMENT = "RUN_ASSESSMENT"
    GENERATE_REPORT = "GENERATE_REPORT"
    ADVANCE_CONCEPT = "ADVANCE_CONCEPT"
    DEFER_GAP = "DEFER_GAP"
    PAUSE_SESSION = "PAUSE_SESSION"
    COMPLETE_SESSION = "COMPLETE_SESSION"


class DifficultyLevel(int, Enum):
    FOUNDATION = 1
    BASIC = 2
    INTERMEDIATE = 3
    APPLICATION = 4
    ADVANCED = 5


class TeachingDecision(BaseModel):
    """Deterministic teaching decision emitted by the Harness / Policy Engine."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_state: SessionState
    action: ActionType
    reason: str
    concept: str
    difficulty: DifficultyLevel = DifficultyLevel.BASIC
    teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION
    visual_strategy: str = "diagram"
    language: str = "en"
    next_state: SessionState
    requires_video: bool = True
    requires_question: bool = False
    confidence: float = 1.0
    evidence_refs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeachingEvent(BaseModel):
    """Event log record for session auditability and state history."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    from_state: SessionState
    to_state: SessionState
    trigger_action: ActionType
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConceptMasterySnapshot(BaseModel):
    concept: str
    mastery: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    attempts: int = 0
    correct_count: int = 0
    last_practiced_at: Optional[datetime] = None


class ActiveMisconception(BaseModel):
    misconception_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    misconception_type: str
    belief: str = "Learner exhibits diagnostic misconception"
    evidence_from_answer: str = "Diagnostic profile evidence"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    severity: str = "moderate"
    prerequisite_gap: Optional[str] = None
    recommended_intervention: Optional[str] = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False



class TeachingSessionState(BaseModel):
    """Durable state of a teaching session."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    lesson_id: str
    topic: str
    subject: str = "physics"
    language: str = "en"
    learner_level: str = "beginner"
    current_state: SessionState = SessionState.START
    previous_state: Optional[SessionState] = None
    current_concept: str
    current_concept_index: int = 0
    concepts_list: List[str] = Field(default_factory=list)
    concept_mastery: Dict[str, float] = Field(default_factory=dict)
    concept_snapshots: Dict[str, ConceptMasterySnapshot] = Field(default_factory=dict)
    active_misconceptions: List[ActiveMisconception] = Field(default_factory=list)
    resolved_misconceptions: List[ActiveMisconception] = Field(default_factory=list)
    current_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION
    strategy_history: List[TeachingStrategy] = Field(default_factory=list)
    current_difficulty: DifficultyLevel = DifficultyLevel.BASIC
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    time_remaining_minutes: int = 10
    total_time_minutes: int = 10
    current_segment_id: Optional[str] = None
    current_question_id: Optional[str] = None
    events_history: List[TeachingEvent] = Field(default_factory=list)
    decisions_history: List[TeachingDecision] = Field(default_factory=list)
    version: int = 1
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

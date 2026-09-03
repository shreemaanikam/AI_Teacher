"""
Data Models and Schemas for Module 7 (Interactive Assessment + Misconception Engine).
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.harness.session import DifficultyLevel, TeachingStrategy


class QuestionType(str, Enum):
    MCQ = "MCQ"
    CONCEPTUAL = "CONCEPTUAL"
    SHORT_ANSWER = "SHORT_ANSWER"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    APPLICATION = "APPLICATION"
    EXPLAIN_IN_OWN_WORDS = "EXPLAIN_IN_OWN_WORDS"
    SCENARIO = "SCENARIO"


class EvaluationVerdict(str, Enum):
    CORRECT = "CORRECT"
    PARTIALLY_CORRECT = "PARTIALLY_CORRECT"
    INCORRECT = "INCORRECT"
    MISCONCEPTION = "MISCONCEPTION"
    UNCERTAIN = "UNCERTAIN"


class QuestionOption(BaseModel):
    id: str
    text: str
    is_correct: bool = False
    misconception_target: Optional[str] = None
    feedback: Optional[str] = None


class AnswerRubric(BaseModel):
    criteria: List[str] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)
    anti_patterns: List[str] = Field(default_factory=list)
    formula: Optional[str] = None
    expected_numerical_value: Optional[float] = None
    numerical_tolerance: float = 0.05
    units: Optional[str] = None


class MisconceptionTarget(BaseModel):
    misconception_type: str
    trigger_patterns: List[str] = Field(default_factory=list)
    explanation: str
    remediation_strategy: TeachingStrategy = TeachingStrategy.SIMPLE_ANALOGY


class Question(BaseModel):
    """Rich question definition with structured pedagogical metadata."""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    concept: str
    prerequisite_concepts: List[str] = Field(default_factory=list)
    type: QuestionType = QuestionType.CONCEPTUAL
    difficulty: DifficultyLevel = DifficultyLevel.BASIC
    prompt: str
    options: Optional[List[QuestionOption]] = None
    expected_answer: str
    rubric: AnswerRubric = Field(default_factory=AnswerRubric)
    misconception_targets: List[MisconceptionTarget] = Field(default_factory=list)
    learning_objective: str = ""
    language: str = "en"
    is_checkpoint: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MisconceptionRecord(BaseModel):
    """Detailed diagnosis of a student misconception."""
    misconception_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    misconception_type: str
    belief: str
    evidence_from_answer: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.85)
    severity: str = "moderate"  # low, moderate, severe
    prerequisite_gap: Optional[str] = None
    recommended_intervention: Optional[str] = None
    recommended_strategy: TeachingStrategy = TeachingStrategy.SIMPLE_ANALOGY
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnswerEvaluation(BaseModel):
    """Comprehensive evaluation result for a student response."""
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    student_id: str
    student_answer: str
    verdict: EvaluationVerdict
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    feedback: str
    rubric_matches: List[str] = Field(default_factory=list)
    rubric_misses: List[str] = Field(default_factory=list)
    misconception: Optional[MisconceptionRecord] = None
    deterministic_validation: bool = False
    evaluator_reason: str = ""
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterventionPlan(BaseModel):
    """Pedagogical intervention crafted to resolve a specific misconception."""
    intervention_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    misconception_type: str
    concept: str
    previous_strategy: TeachingStrategy
    new_strategy: TeachingStrategy
    reason_for_change: str
    analogy_prompt: Optional[str] = None
    visual_type: str = "diagram"
    recheck_question_type: QuestionType = QuestionType.CONCEPTUAL
    steps: List[str] = Field(default_factory=list)

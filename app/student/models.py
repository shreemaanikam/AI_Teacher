"""
Domain Models and Schemas for Phase 9: Personalized College Student Platform.
Supports student dashboard, exam study planning, dynamic replanning,
tasks, deadlines, adaptive assignments, and evaluation.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class StudyBlock(BaseModel):
    block_id: str = Field(default_factory=lambda: f"blk_{uuid.uuid4().hex[:6]}")
    day_number: int = 1
    date: str  # YYYY-MM-DD
    title: str
    concepts: List[str] = Field(default_factory=list)
    focus_type: str = "CONCEPTS"  # CONCEPTS, WEAK_REVISION, PRACTICE, MOCK_TEST, FINAL_REVIEW
    allocated_hours: float = 2.0
    completed: bool = False
    priority: str = "HIGH"  # HIGH, MEDIUM, LOW


class ExamPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"eplan_{uuid.uuid4().hex[:8]}")
    student_id: str
    course_id: str
    course_name: str
    exam_date: str
    target_score: str = "90%"
    available_hours_per_day: float = 2.0
    total_days: int = 7
    schedule: List[StudyBlock] = Field(default_factory=list)
    status: str = "ACTIVE"
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"tsk_{uuid.uuid4().hex[:8]}")
    student_id: str
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    concept: Optional[str] = None
    title: str
    task_type: str = "REVISION"  # REVISION, PRACTICE, ASSIGNMENT, EXAM_PREP
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    deadline: Optional[str] = None
    estimated_duration_minutes: int = 30
    status: str = "TODO"  # TODO, IN_PROGRESS, COMPLETED, OVERDUE
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssignmentQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: f"aq_{uuid.uuid4().hex[:6]}")
    prompt: str
    question_type: str = "SHORT_ANSWER"  # MCQ, NUMERICAL, SHORT_ANSWER, CODING
    options: Optional[List[str]] = None
    expected_answer: str
    rubric: List[str] = Field(default_factory=list)
    marks: float = 10.0


class StudentAssignment(BaseModel):
    assignment_id: str = Field(default_factory=lambda: f"asgn_{uuid.uuid4().hex[:8]}")
    student_id: str
    course_id: Optional[str] = None
    course_name: str
    concept: str
    title: str
    assignment_type: str = "PRACTICE_SET"  # MCQ, NUMERICAL, SHORT_ANSWER, CODING, DEBUGGING, CASE_STUDY
    difficulty: str = "INTERMEDIATE"  # EASY, INTERMEDIATE, ADVANCED
    questions: List[AssignmentQuestion] = Field(default_factory=list)
    deadline: Optional[str] = None
    status: str = "ASSIGNED"  # ASSIGNED, SUBMITTED, GRADED
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssignmentSubmission(BaseModel):
    submission_id: str = Field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    assignment_id: str
    student_id: str
    answers: Dict[str, str] = Field(default_factory=dict)
    score: float = 0.0
    max_score: float = 100.0
    verdict: str = "PROFICIENT"
    feedback: str = ""
    misconceptions: List[str] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentDashboardData(BaseModel):
    student_id: str
    name: str
    college: str
    degree: str
    year: int
    semester: int
    what_should_i_study_now: str
    continue_learning: Optional[Dict[str, Any]] = None
    today_plan: List[Dict[str, Any]] = Field(default_factory=list)
    upcoming_deadlines: List[Dict[str, Any]] = Field(default_factory=list)
    exam_countdown: List[Dict[str, Any]] = Field(default_factory=list)
    weak_concepts: List[Dict[str, Any]] = Field(default_factory=list)
    recent_progress: Dict[str, Any] = Field(default_factory=dict)
    recommended_next_topic: str = ""
    exam_readiness_percentage: float = 0.0
    enrolled_courses: List[Dict[str, Any]] = Field(default_factory=list)


class PracticalTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"ptask_{uuid.uuid4().hex[:8]}")
    student_id: str
    course_id: Optional[str] = None
    subject: str  # Machine Learning, DBMS, Data Structures, Physics
    topic: str
    title: str
    prompt: str
    starter_code: str
    expected_output_or_rubric: str
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    difficulty: str = "INTERMEDIATE"  # EASY, INTERMEDIATE, ADVANCED
    status: str = "ASSIGNED"  # ASSIGNED, SUBMITTED, EVALUATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PracticalSubmission(BaseModel):
    submission_id: str = Field(default_factory=lambda: f"psub_{uuid.uuid4().hex[:8]}")
    task_id: str
    student_id: str
    code_submission: str
    score: float = 0.0
    verdict: str = "PASS"  # PASS, PARTIAL, FAIL
    feedback: str = ""
    tests_passed: int = 0
    total_tests: int = 0
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentDoubt(BaseModel):
    doubt_id: str = Field(default_factory=lambda: f"dbt_{uuid.uuid4().hex[:8]}")
    student_id: str
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    concept: str
    question_text: str
    resolved_context: str = ""
    teacher_response: str = ""
    status: str = "RESOLVED"  # RESOLVED, UNRESOLVED, BOOKMARKED, MASTERED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeachingInterruptionState(BaseModel):
    session_id: str
    student_id: str
    concept: str
    paused_timestamp: float
    doubt_text: str
    teacher_answer: str
    resumed: bool = False
    interrupted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeachingControlResult(BaseModel):
    action: str
    concept: str
    language: str = "en"
    explanation: str
    avatar_script: str
    visual_action: Optional[Dict[str, Any]] = None
    exercise: Optional[Dict[str, Any]] = None


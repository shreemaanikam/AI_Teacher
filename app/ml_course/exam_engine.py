"""
STAGE ML-COURSE-21: Machine Learning Exam Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Generates adaptive exam sessions (5 min, 20 min, 60 min) and 7-day revision schedules
grounded in the 28 identified college exam topics, dynamically weighting weak concepts.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import ExamTopic, SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.problem_bank import MLProblemBank


class ExamQuestionItem(BaseModel):
    question_id: str
    unit: int
    concept_id: str
    topic: str
    question_type: str  # MCQ, SHORT_ANSWER, NUMERICAL, DERIVATION, ALGORITHM
    question_text: str
    allocated_minutes: int
    marks: int
    importance: str = "HIGH"
    source_refs: List[SourceRef] = Field(default_factory=list)


class ExamSession(BaseModel):
    session_id: str
    duration_minutes: int
    total_marks: int
    units_covered: List[int]
    questions: List[ExamQuestionItem]
    time_allocation: Dict[str, int]
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class DaySchedule(BaseModel):
    day: int
    title: str
    units_covered: List[int]
    allocated_hours: float
    priority_topics: List[str]
    tasks: List[str]
    mock_test_duration_minutes: int = 0


class SevenDayRevisionPlan(BaseModel):
    target_score: int
    hours_per_day: float
    daily_schedules: List[DaySchedule]
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLExamEngine:
    """
    Orchestrates time-budgeted exam sessions and revision timetables.
    """

    _instance: Optional[MLExamEngine] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLExamEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_exam_session(
        self,
        duration_minutes: int,
        student_weak_concepts: Optional[List[str]] = None,
    ) -> ExamSession:
        if duration_minutes not in (5, 20, 60):
            raise ValueError(f"Supported exam durations are 5, 20, or 60 minutes. Received: {duration_minutes}")

        weak_set = set(student_weak_concepts or [])
        course = self._kb.course

        # Collect candidate exam topics
        candidate_topics: List[ExamTopic] = []
        for u in course.units.values():
            candidate_topics.extend(u.exam_topics)

        # Sort so weak concepts or EXAM_CRITICAL come first
        def topic_weight(t: ExamTopic) -> int:
            score = 0
            if t.concept_id in weak_set:
                score += 10
            if t.importance == "EXAM_CRITICAL":
                score += 5
            elif t.importance == "HIGH":
                score += 2
            return score

        candidate_topics.sort(key=topic_weight, reverse=True)

        questions: List[ExamQuestionItem] = []
        time_alloc: Dict[str, int] = {}
        total_time = 0
        total_marks = 0

        # Build questions depending on duration
        if duration_minutes == 5:
            # 2 quick high-yield questions (2.5 mins each, 5 marks each)
            selected = candidate_topics[:2]
            for idx, t in enumerate(selected):
                q = ExamQuestionItem(
                    question_id=f"exam_q5_{idx+1}",
                    unit=t.unit,
                    concept_id=t.concept_id,
                    topic=t.concept,
                    question_type="SHORT_ANSWER",
                    question_text=f"Explain {t.concept} and state its key mathematical formulation or operational principle.",
                    allocated_minutes=2,
                    marks=5,
                    importance=t.importance,
                    source_refs=t.source_refs,
                )
                questions.append(q)
                total_time += 2
                total_marks += 5
            time_alloc["Core Concepts Review"] = 5

        elif duration_minutes == 20:
            # 4 questions across units (1 numerical, 2 conceptual, 1 algorithm)
            selected = candidate_topics[:4]
            # Include at least 1 numerical
            probs = MLProblemBank.get_all_problems()
            q_num = ExamQuestionItem(
                question_id="exam_q20_num",
                unit=probs[0].unit,
                concept_id=probs[0].concept_id,
                topic=probs[0].topic,
                question_type="NUMERICAL",
                question_text=probs[0].question,
                allocated_minutes=8,
                marks=10,
                importance="EXAM_CRITICAL",
                source_refs=probs[0].source_refs,
            )
            questions.append(q_num)
            total_time += 8
            total_marks += 10

            for idx, t in enumerate(selected[:3]):
                q = ExamQuestionItem(
                    question_id=f"exam_q20_c_{idx+1}",
                    unit=t.unit,
                    concept_id=t.concept_id,
                    topic=t.concept,
                    question_type="CONCEPTUAL",
                    question_text=f"Explain {t.concept} with practical significance.",
                    allocated_minutes=4,
                    marks=5,
                    importance=t.importance,
                    source_refs=t.source_refs,
                )
                questions.append(q)
                total_time += 4
                total_marks += 5

            time_alloc["Numerical Problem"] = 8
            time_alloc["Conceptual Theory"] = 12

        else:  # 60 minutes
            # Full comprehensive exam covering all 5 units
            for u_num in range(1, 6):
                u_topics = [t for t in candidate_topics if t.unit == u_num]
                top_t = u_topics[0] if u_topics else candidate_topics[0]
                q_theory = ExamQuestionItem(
                    question_id=f"exam_q60_u{u_num}_t",
                    unit=u_num,
                    concept_id=top_t.concept_id,
                    topic=top_t.concept,
                    question_type="DERIVATION",
                    question_text=f"Provide a comprehensive derivation and explanation of {top_t.concept}.",
                    allocated_minutes=8,
                    marks=10,
                    importance=top_t.importance,
                    source_refs=top_t.source_refs,
                )
                questions.append(q_theory)
                total_marks += 10

            # Add two numerical problems
            probs = MLProblemBank.get_all_problems()
            for p in probs[:2]:
                q_p = ExamQuestionItem(
                    question_id=f"exam_q60_num_{p.problem_id}",
                    unit=p.unit,
                    concept_id=p.concept_id,
                    topic=p.topic,
                    question_type="NUMERICAL",
                    question_text=p.question,
                    allocated_minutes=10,
                    marks=10,
                    importance="EXAM_CRITICAL",
                    source_refs=p.source_refs,
                )
                questions.append(q_p)
                total_marks += 10

            time_alloc["Section A: 5-Unit Core Theory"] = 40
            time_alloc["Section B: Applied Numericals"] = 20

        units_covered = sorted(list({q.unit for q in questions}))

        return ExamSession(
            session_id=f"session_{duration_minutes}m",
            duration_minutes=duration_minutes,
            total_marks=total_marks,
            units_covered=units_covered,
            questions=questions,
            time_allocation=time_alloc,
            verification_status=VerificationStatus.VERIFIED,
        )

    def generate_7day_revision_schedule(
        self,
        target_score: int = 90,
        available_hours_per_day: float = 2.0,
        weak_units: Optional[List[int]] = None,
    ) -> SevenDayRevisionPlan:
        """
        Creates an intelligent 7-day collegiate review roadmap allocating additional
        time to declared weak units.
        """
        weak_u = set(weak_units or [])
        days: List[DaySchedule] = []

        day_unit_map = {
            1: (1, "Unit I Foundation: Linear Regression, Inductive Bias & Evaluation"),
            2: (2, "Unit II Supervised Learning: Decision Trees, Perceptron & SVM"),
            3: (3, "Unit III Deep Learning: Multilayer Networks, Backprop & CNNs"),
            4: (4, "Unit IV Unsupervised Learning: K-Means, GMM & PCA"),
            5: (5, "Unit V Optimization & RL: Q-Learning, Least Squares & Responsible AI"),
        }

        for day in range(1, 6):
            u_num, title = day_unit_map[day]
            allocated = available_hours_per_day * (1.25 if u_num in weak_u else 1.0)
            u_obj = self._kb.course.units[u_num]
            days.append(
                DaySchedule(
                    day=day,
                    title=title,
                    units_covered=[u_num],
                    allocated_hours=round(allocated, 2),
                    priority_topics=[c.name for c in u_obj.concepts[:3]],
                    tasks=[
                        f"Review {u_obj.title} core formulas",
                        f"Solve worked numericals from {u_obj.unit_code}",
                        f"Attempt 20-minute timed checkpoint test",
                    ],
                    mock_test_duration_minutes=20,
                )
            )

        # Day 6: Cross-Unit Problem Bank & Weak Concept Remediation
        days.append(
            DaySchedule(
                day=6,
                title="Cross-Unit Synthesis, Problem Bank & Weak Spot Remediation",
                units_covered=[1, 2, 3, 4, 5],
                allocated_hours=available_hours_per_day,
                priority_topics=["Backpropagation calculation", "K-Means iterations", "Q-Learning Bellman equation"],
                tasks=[
                    "Solve all remaining numericals from college problem sheets",
                    "Conduct formula recall quiz across all 5 units",
                ],
                mock_test_duration_minutes=30,
            )
        )

        # Day 7: Comprehensive 60-Minute Mock Exam
        days.append(
            DaySchedule(
                day=7,
                title="Full Comprehensive Mock Exam & Final High-Yield Revision",
                units_covered=[1, 2, 3, 4, 5],
                allocated_hours=available_hours_per_day,
                priority_topics=["All Units Gold Exam Topics"],
                tasks=[
                    "Take full 60-minute mock examination",
                    "Review grading feedback and remedy identified misconceptions",
                ],
                mock_test_duration_minutes=60,
            )
        )

        return SevenDayRevisionPlan(
            target_score=target_score,
            hours_per_day=available_hours_per_day,
            daily_schedules=days,
            verification_status=VerificationStatus.VERIFIED,
        )

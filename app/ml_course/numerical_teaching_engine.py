"""
STAGE ML-COURSE-20: Numerical Teaching & Interactive Doubt Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Delivers step-by-step interactive numerical walkthroughs and resolves student doubts
(formula justification, intermediate calculation, parameter origin) grounded in college materials.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef, VerificationStatus, ProblemItem
from app.ml_course.problem_bank import MLProblemBank
from app.ml_course.numerical_engine import MLNumericalEngine
from app.ml_course.knowledge import CourseKnowledgeBase


class NumericalLessonPlan(BaseModel):
    problem_id: str
    topic: str
    question: str
    given_data: Dict[str, Any]
    formula: str
    step_by_step_walkthrough: List[str]
    final_answer: str
    source_refs: List[SourceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLNumericalTeachingEngine:
    """
    Teaches college Machine Learning numerical problems step by step and answers student doubts.
    """

    _instance: Optional[MLNumericalTeachingEngine] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLNumericalTeachingEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def teach_numerical_problem(self, problem_id: str) -> NumericalLessonPlan:
        prob = MLProblemBank.get_problem(problem_id)
        if not prob:
            raise ValueError(f"Numerical problem not found: {problem_id}")

        return NumericalLessonPlan(
            problem_id=prob.problem_id,
            topic=prob.topic,
            question=prob.question,
            given_data=prob.given_data,
            formula=prob.formula,
            step_by_step_walkthrough=prob.solution_steps,
            final_answer=prob.final_answer,
            source_refs=prob.source_refs,
            verification_status=prob.verification_status,
        )

    def answer_student_numerical_doubt(
        self,
        problem_id: str,
        doubt: str,
    ) -> Dict[str, Any]:
        """
        Resolves student queries:
        - "Why this formula?"
        - "How did you calculate this?"
        - "Why did the centroid change?"
        - "Why is this value used?"
        """
        prob = MLProblemBank.get_problem(problem_id)
        if not prob:
            raise ValueError(f"Unknown problem: {problem_id}")

        q_low = doubt.lower()

        if "why this formula" in q_low or "why formula" in q_low or "which formula" in q_low:
            answer = (
                f"We use the formula '{prob.formula}' because the problem on {prob.topic} "
                f"in Unit {prob.unit} requires evaluating distances/probabilities directly according to standard notes specification."
            )
            category = "FORMULA_JUSTIFICATION"

        elif "centroid change" in q_low or "why centroid" in q_low:
            answer = (
                "In K-Means, after all data points are assigned to their nearest cluster, "
                "the centroid is updated by computing the arithmetic mean (average) of all points currently assigned to that cluster."
            )
            category = "CENTROID_UPDATE_EXPLANATION"

        elif "how did you calculate" in q_low or "how calculate" in q_low or "step" in q_low:
            # Highlight first 3 solution steps
            steps_preview = " -> ".join(prob.solution_steps[:3])
            answer = f"The calculation proceeds in sequential steps: {steps_preview}. Then we arrive at {prob.final_answer}."
            category = "CALCULATION_STEP_EXPLANATION"

        elif "why is this value" in q_low or "why value" in q_low or "given" in q_low:
            given_str = ", ".join([f"{k}: {v}" for k, v in prob.given_data.items() if not isinstance(v, list)])
            answer = f"This value is taken directly from the problem statement: {given_str}."
            category = "PARAMETER_SOURCE_EXPLANATION"

        else:
            answer = (
                f"For {prob.topic}, please refer to the step-by-step solution: "
                f"First step: '{prob.solution_steps[0]}', leading to final answer '{prob.final_answer}'."
            )
            category = "GENERAL_NUMERICAL_GUIDANCE"

        return {
            "problem_id": problem_id,
            "doubt_category": category,
            "answer": answer,
            "source_document": prob.source_document,
            "source_page": prob.source_page,
            "is_grounded": True,
        }

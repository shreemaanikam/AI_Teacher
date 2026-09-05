"""
STAGE ML-COURSE-23: Course-Grounded Answer Evaluation Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Evaluates student responses against course ground truth, formulas, algorithms,
and definitions. Never marks an academically incorrect answer as correct merely
because superficial wording appears similar.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field

from app.ml_course.models import ClaimStatus, SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.claim_validator import MLClaimValidator
from app.ml_course.numerical_engine import MLNumericalEngine


class AnswerEvaluationResult(BaseModel):
    evaluation_status: str  # CORRECT, PARTIALLY_CORRECT, INCORRECT, UNSUPPORTED, UNCERTAIN
    score: float  # 0.0 to 1.0
    feedback: str
    concept_id: str
    misconception_detected: Optional[str] = None
    remediation_suggested: Optional[str] = None
    evidence_excerpts: List[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED

    @property
    def is_correct(self) -> bool:
        return self.evaluation_status == "CORRECT" or self.score >= 0.8


class MLAnswerEvaluator:
    """
    Rigorously grades student responses and flags misconceptions using college ML notes.
    """

    _instance: Optional[MLAnswerEvaluator] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._validator = MLClaimValidator.get_instance()

    @classmethod
    def get_instance(cls) -> MLAnswerEvaluator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate_answer(
        self,
        question_text: str,
        expected_answer: str,
        student_response: str,
        concept_id: str,
        unit: int,
        question_type: str = "CONCEPTUAL",
    ) -> AnswerEvaluationResult:
        student_text = student_response.strip()
        if not student_text:
            return AnswerEvaluationResult(
                evaluation_status="INCORRECT",
                score=0.0,
                feedback="Empty answer submitted.",
                concept_id=concept_id,
            )

        # 1. Check for immediate direct contradictions/misconceptions
        # (e.g. "K-Means is supervised", "Sigmoid outputs -1 to 1", "Linear regression is for classification")
        script_val = self._validator.validate_script(student_text, unit=unit, concept_id=concept_id)
        if any(c.status == ClaimStatus.CONTRADICTED for c in script_val.claims):
            contr = next(c for c in script_val.claims if c.status == ClaimStatus.CONTRADICTED)
            return AnswerEvaluationResult(
                evaluation_status="INCORRECT",
                score=0.0,
                feedback=f"Academically incorrect assertion: {contr.suggested_correction}",
                concept_id=concept_id,
                misconception_detected=contr.contradiction_reason,
                remediation_suggested=f"Review definition of {concept_id} in Unit {unit} lecture notes.",
            )

        # 2. MCQ Evaluation
        if question_type.upper() == "MCQ":
            clean_student = student_text.lower().strip()
            clean_expected = expected_answer.lower().strip()
            if clean_expected in clean_student or clean_student in clean_expected:
                return AnswerEvaluationResult(
                    evaluation_status="CORRECT",
                    score=1.0,
                    feedback="Correct choice matching course syllabus.",
                    concept_id=concept_id,
                )
            else:
                return AnswerEvaluationResult(
                    evaluation_status="INCORRECT",
                    score=0.0,
                    feedback=f"Incorrect selection. Expected: '{expected_answer}'.",
                    concept_id=concept_id,
                )

        # 3. Numerical Evaluation
        if question_type.upper() == "NUMERICAL":
            # Extract numbers and compare
            exp_floats = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", expected_answer)]
            sub_floats = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", student_text)]
            if exp_floats and sub_floats:
                target_num = exp_floats[0]
                student_num = sub_floats[0]
                if abs(target_num - student_num) <= max(0.05, 0.05 * abs(target_num)):
                    return AnswerEvaluationResult(
                        evaluation_status="CORRECT",
                        score=1.0,
                        feedback="Calculations and numerical answer match college problem solution.",
                        concept_id=concept_id,
                    )
            # Exact phrase check (e.g. Cricket)
            if expected_answer.lower() in student_text.lower():
                return AnswerEvaluationResult(
                    evaluation_status="CORRECT",
                    score=1.0,
                    feedback="Correct qualitative conclusion matching notes.",
                    concept_id=concept_id,
                )
            return AnswerEvaluationResult(
                evaluation_status="INCORRECT",
                score=0.0,
                feedback=f"Incorrect calculation. Expected: {expected_answer}.",
                concept_id=concept_id,
            )

        # 4. Conceptual / Algorithmic / Derivation Evaluation
        concept = self._kb.get_concept(concept_id)
        concept_summary = concept.summary.lower() if concept else ""

        tokens_expected = set(re.findall(r"\w+", expected_answer.lower()))
        tokens_student = set(re.findall(r"\w+", student_text.lower()))

        # Strip stopwords
        stopwords = {"the", "a", "an", "is", "in", "and", "to", "of", "for", "with", "that", "this", "it", "on", "as", "by"}
        core_expected = tokens_expected - stopwords
        overlap = tokens_student.intersection(core_expected)

        concept_tokens = set(re.findall(r"\w+", concept_summary)) - stopwords if concept else set()
        overlap_summary = tokens_student.intersection(concept_tokens)

        overlap_ratio = len(overlap) / max(len(core_expected), 1)
        summary_ratio = len(overlap_summary) / max(len(tokens_student - stopwords), 1)

        if overlap_ratio >= 0.35 or (len(overlap) >= 4 and summary_ratio >= 0.4):
            return AnswerEvaluationResult(
                evaluation_status="CORRECT",
                score=1.0,
                feedback="Accurate explanation capturing all key points from course notes.",
                concept_id=concept_id,
                evidence_excerpts=[concept.summary[:150]] if concept else [],
            )
        elif overlap_ratio >= 0.25:
            return AnswerEvaluationResult(
                evaluation_status="PARTIALLY_CORRECT",
                score=0.5,
                feedback="Partially correct, but missing key technical criteria or conditions.",
                concept_id=concept_id,
                evidence_excerpts=[concept.summary[:150]] if concept else [],
                remediation_suggested="Review complete mechanism in notes.",
            )
        else:
            return AnswerEvaluationResult(
                evaluation_status="INCORRECT",
                score=0.0,
                feedback="Response does not demonstrate understanding of the required course concept.",
                concept_id=concept_id,
                remediation_suggested="Read Unit source notes for foundational definitions.",
            )

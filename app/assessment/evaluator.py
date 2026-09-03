"""
Answer Evaluator for Module 7 (Assessment & Misconception Engine).
Multi-stage evaluation pipeline combining deterministic numeric validation, semantic rubric matching,
and misconception classification.
"""

from __future__ import annotations
import math
import re
from typing import Optional
from app.assessment.models import (
    AnswerEvaluation,
    EvaluationVerdict,
    Question,
    QuestionType,
    MisconceptionRecord,
)
from app.assessment.misconceptions import MisconceptionDetector


class AnswerEvaluator:
    """
    Evaluates student answers through a rigorous multi-stage pipeline:
    1. Normalization
    2. Deterministic numeric verification (if applicable)
    3. MCQ selection resolution (if applicable)
    4. Semantic rubric & key-term evaluation
    5. Misconception detection
    6. Confidence & scoring synthesis
    """

    def __init__(self, detector: Optional[MisconceptionDetector] = None):
        self.detector = detector or MisconceptionDetector()

    def normalize_text(self, text: str) -> str:
        """Strips punctuation, normalizes whitespace and lowers case."""
        cleaned = re.sub(r"[^\w\s\.\-\+\/\*]", " ", text)
        return " ".join(cleaned.lower().split())

    def evaluate_numerical(self, question: Question, student_answer: str) -> Optional[tuple[bool, float, str]]:
        """
        Deterministically verifies numerical answers, formulas, and tolerance boundaries.
        Returns (is_correct, score, feedback) or None if not numerical.
        """
        rubric = question.rubric
        if rubric.expected_numerical_value is None:
            return None

        # Extract numerical tokens from student answer
        matches = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", student_answer)
        if not matches:
            return (
                False,
                0.0,
                f"No numerical value found in answer. Expected approximately {rubric.expected_numerical_value} {rubric.units or ''}.",
            )

        # Check last or closest extracted value
        student_val = float(matches[-1])
        expected_val = rubric.expected_numerical_value
        tol = rubric.numerical_tolerance * abs(expected_val) if expected_val != 0 else 0.01

        diff = abs(student_val - expected_val)
        is_exact = diff <= 1e-5
        is_within_tol = diff <= tol

        if is_within_tol:
            unit_hint = f" {rubric.units}" if rubric.units else ""
            return (
                True,
                1.0,
                f"Correct calculation! {student_val}{unit_hint} matches the expected value ({expected_val}{unit_hint}).",
            )
        else:
            return (
                False,
                0.0,
                f"Incorrect numerical result. Calculated {student_val}, expected {expected_val} (tolerance ±{tol:.2f}).",
            )

    def evaluate_mcq(self, question: Question, student_answer: str) -> Optional[tuple[bool, float, str, Optional[str]]]:
        """Evaluates multiple-choice selections."""
        if not question.options or question.type != QuestionType.MCQ:
            return None

        clean_ans = student_answer.strip().lower()
        matched_opt = None
        for opt in question.options:
            if opt.id.lower() == clean_ans or opt.text.lower() == clean_ans:
                matched_opt = opt
                break

        if not matched_opt:
            # Substring match
            for opt in question.options:
                if opt.id.lower() in clean_ans or opt.text.lower() in clean_ans:
                    matched_opt = opt
                    break

        if matched_opt:
            is_correct = matched_opt.is_correct
            score = 1.0 if is_correct else 0.0
            feedback = matched_opt.feedback or ("Correct selection!" if is_correct else "Incorrect selection.")
            return (is_correct, score, feedback, matched_opt.misconception_target)

        return None

    def evaluate(
        self,
        question: Question,
        student_answer: str,
        student_id: str = "default_student",
        subject: str = "physics",
    ) -> AnswerEvaluation:
        """
        Executes the full evaluation pipeline for a student response.
        """
        normalized_answer = self.normalize_text(student_answer)

        # Stage 1: Check Misconception First
        misconception = self.detector.detect_misconception(
            question=question,
            student_answer=student_answer,
            subject=subject,
        )

        # Stage 2: Deterministic Numerical Check
        num_res = self.evaluate_numerical(question, student_answer)
        if num_res is not None:
            is_correct, score, feedback = num_res
            verdict = EvaluationVerdict.CORRECT if is_correct else (
                EvaluationVerdict.MISCONCEPTION if misconception else EvaluationVerdict.INCORRECT
            )
            return AnswerEvaluation(
                question_id=question.question_id,
                student_id=student_id,
                student_answer=student_answer,
                verdict=verdict,
                score=score,
                confidence=1.0,
                feedback=feedback,
                misconception=misconception if not is_correct else None,
                deterministic_validation=True,
                evaluator_reason="Deterministic calculation verification against rubric numerical tolerance.",
            )

        # Stage 3: MCQ Evaluation
        mcq_res = self.evaluate_mcq(question, student_answer)
        if mcq_res is not None:
            is_correct, score, feedback, _ = mcq_res
            verdict = EvaluationVerdict.CORRECT if is_correct else (
                EvaluationVerdict.MISCONCEPTION if misconception else EvaluationVerdict.INCORRECT
            )
            return AnswerEvaluation(
                question_id=question.question_id,
                student_id=student_id,
                student_answer=student_answer,
                verdict=verdict,
                score=score,
                confidence=1.0,
                feedback=feedback,
                misconception=misconception if not is_correct else None,
                deterministic_validation=True,
                evaluator_reason="Direct MCQ option key and rubric comparison.",
            )

        # Stage 4: Semantic & Rubric Evaluation for Conceptual / Short-Answer
        rubric = question.rubric
        rubric_matches = []
        rubric_misses = []

        # Key terms check
        term_matches = [kt for kt in rubric.key_terms if kt.lower() in normalized_answer]
        rubric_matches.extend(term_matches)
        for kt in rubric.key_terms:
            if kt.lower() not in normalized_answer:
                rubric_misses.append(f"Missing key concept: '{kt}'")

        # Anti-patterns check
        found_anti = [ap for ap in rubric.anti_patterns if ap.lower() in normalized_answer]

        # Calculate semantic score
        total_criteria = max(1, len(rubric.key_terms))
        semantic_score = len(term_matches) / total_criteria

        if found_anti:
            semantic_score = max(0.0, semantic_score - 0.5)

        # Determine verdict
        if misconception is not None:
            verdict = EvaluationVerdict.MISCONCEPTION
            score = 0.1
            feedback = f"Misconception identified: {misconception.belief}. {misconception.recommended_intervention or ''}"
            confidence = misconception.confidence
        elif semantic_score >= 0.8:
            verdict = EvaluationVerdict.CORRECT
            score = 1.0
            feedback = "Excellent! Your explanation accurately captures the core scientific principles."
            confidence = 0.95
        elif semantic_score >= 0.4:
            verdict = EvaluationVerdict.PARTIALLY_CORRECT
            score = round(semantic_score, 2)
            feedback = f"Partially correct. You noted {', '.join(term_matches)}, but make sure to explain: {', '.join(rubric_misses)}."
            confidence = 0.85
        else:
            verdict = EvaluationVerdict.INCORRECT
            score = round(semantic_score, 2)
            feedback = f"Not quite right. The expected answer involves: {question.expected_answer}."
            confidence = 0.90

        return AnswerEvaluation(
            question_id=question.question_id,
            student_id=student_id,
            student_answer=student_answer,
            verdict=verdict,
            score=score,
            confidence=confidence,
            feedback=feedback,
            rubric_matches=rubric_matches,
            rubric_misses=rubric_misses,
            misconception=misconception if verdict == EvaluationVerdict.MISCONCEPTION else None,
            deterministic_validation=False,
            evaluator_reason=f"Semantic rubric matched {len(term_matches)}/{len(rubric.key_terms)} key terms.",
        )

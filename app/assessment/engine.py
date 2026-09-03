"""
Assessment Engine for Module 7.
Central coordinator for question generation, answer evaluation, misconception diagnostics, and final reports.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional
import uuid

from app.assessment.models import (
    Question,
    QuestionType,
    QuestionOption,
    AnswerRubric,
    MisconceptionTarget,
    AnswerEvaluation,
    EvaluationVerdict,
    InterventionPlan,
    MisconceptionRecord,
)
from app.assessment.evaluator import AnswerEvaluator
from app.assessment.misconceptions import MisconceptionDetector
from app.assessment.interventions import InterventionEngine
from app.assessment.difficulty import AdaptiveDifficultyController
from app.assessment.taxonomy import MisconceptionTaxonomy
from app.harness.session import DifficultyLevel, TeachingStrategy

logger = logging.getLogger(__name__)


class AssessmentEngine:
    """
    High-level engine for interactive educational assessments and misconception diagnostics.
    """

    def __init__(
        self,
        evaluator: Optional[AnswerEvaluator] = None,
        intervention_engine: Optional[InterventionEngine] = None,
        difficulty_controller: Optional[AdaptiveDifficultyController] = None,
    ):
        self.evaluator = evaluator or AnswerEvaluator()
        self.intervention_engine = intervention_engine or InterventionEngine()
        self.difficulty_controller = difficulty_controller or AdaptiveDifficultyController()
        self._questions_store: Dict[str, Question] = {}
        self._initialize_sample_question_bank()

    def store_question(self, question: Question) -> None:
        self._questions_store[question.question_id] = question

    def get_question(self, question_id: str) -> Optional[Question]:
        return self._questions_store.get(question_id)

    def generate_checkpoint_question(
        self,
        lesson_id: str,
        concept: str,
        difficulty: DifficultyLevel = DifficultyLevel.BASIC,
        language: str = "en",
        question_type: QuestionType = QuestionType.CONCEPTUAL,
    ) -> Question:
        """Generates or retrieves a level-appropriate checkpoint question for a concept."""
        # Find matching cached question or instantiate a well-formed question
        for q in self._questions_store.values():
            if q.concept.lower() == concept.lower() and q.difficulty == difficulty and q.is_checkpoint:
                return q

        # Dynamic fallback generation for common topics
        if "ohm" in concept.lower() or "resistance" in concept.lower() or "current" in concept.lower():
            q = Question(
                lesson_id=lesson_id,
                concept=concept,
                prerequisite_concepts=["voltage_concept"],
                type=QuestionType.CONCEPTUAL,
                difficulty=difficulty,
                prompt="According to Ohm's Law (V = I * R), what happens to the current (I) in a circuit if the resistance (R) is doubled while the voltage (V) remains constant?",
                expected_answer="The current is halved because current is inversely proportional to resistance.",
                rubric=AnswerRubric(
                    criteria=["States current decreases or is halved", "Mentions inverse relationship or I = V/R formula"],
                    key_terms=["decrease", "halved", "half", "inversely proportional", "reduces"],
                    anti_patterns=["current increases", "current doubles", "stays same"],
                    formula="I = V / R",
                ),
                misconception_targets=[
                    MisconceptionTarget(
                        misconception_type="inverse_relationship_confusion",
                        trigger_patterns=["current increases", "doubles", "increases", "more current", "doubled"],
                        explanation="Student believes increasing resistance increases electrical current.",
                        remediation_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                    )
                ],
                learning_objective="Understand the inverse relationship between current and resistance in Ohm's Law.",
                language=language,
                is_checkpoint=True,
            )
            self.store_question(q)
            return q

        # Generic question fallback
        q = Question(
            lesson_id=lesson_id,
            concept=concept,
            type=question_type,
            difficulty=difficulty,
            prompt=f"Explain the primary principle behind '{concept}' in your own words.",
            expected_answer=f"Fundamental definition and core characteristics of {concept}.",
            rubric=AnswerRubric(key_terms=[concept.lower()]),
            language=language,
            is_checkpoint=True,
        )
        self.store_question(q)
        return q

    def generate_recheck_question(
        self,
        lesson_id: str,
        concept: str,
        misconception: MisconceptionRecord,
        difficulty: DifficultyLevel = DifficultyLevel.BASIC,
        language: str = "en",
    ) -> Question:
        """Generates a targeted follow-up question specifically testing resolution of the misconception."""
        if "inverse" in misconception.misconception_type.lower():
            q = Question(
                lesson_id=lesson_id,
                concept=concept,
                type=QuestionType.MCQ,
                difficulty=difficulty,
                prompt="If you add a resistor to a circuit, making the total resistance higher, what will the ammeter show happening to the current?",
                options=[
                    QuestionOption(id="A", text="The current decreases", is_correct=True, feedback="Correct! Higher resistance reduces current."),
                    QuestionOption(id="B", text="The current increases", is_correct=False, misconception_target="inverse_relationship_confusion", feedback="Incorrect. Resistance impedes current flow."),
                    QuestionOption(id="C", text="The current remains exactly the same", is_correct=False, feedback="Incorrect. Changing resistance changes current according to I = V / R."),
                ],
                expected_answer="The current decreases",
                rubric=AnswerRubric(
                    key_terms=["decreases", "lower", "reduces"],
                    formula="I = V / R",
                ),
                misconception_targets=[
                    MisconceptionTarget(
                        misconception_type="inverse_relationship_confusion",
                        trigger_patterns=["current increases", "increases", "b", "option b"],
                        explanation="Student still believes resistance increases current.",
                        remediation_strategy=TeachingStrategy.VISUAL_EXPLANATION,
                    )
                ],
                learning_objective="Confirm resolution of inverse current-resistance relationship.",
                language=language,
                is_checkpoint=True,
            )
            self.store_question(q)
            return q

        return self.generate_checkpoint_question(lesson_id, concept, difficulty, language)

    def evaluate_response(
        self,
        question_id: str,
        student_answer: str,
        student_id: str = "student_1",
        subject: str = "physics",
        time_taken_seconds: Optional[float] = None,
    ) -> AnswerEvaluation:
        """Evaluates student response against the question and updates difficulty records."""
        question = self.get_question(question_id)
        if not question:
            raise KeyError(f"Question with ID '{question_id}' not found in assessment store.")

        evaluation = self.evaluator.evaluate(
            question=question,
            student_answer=student_answer,
            student_id=student_id,
            subject=subject,
        )

        is_correct = evaluation.verdict == EvaluationVerdict.CORRECT
        has_misconception = evaluation.misconception is not None

        self.difficulty_controller.record_attempt(
            is_correct=is_correct,
            score=evaluation.score,
            confidence=evaluation.confidence,
            has_misconception=has_misconception,
            difficulty_level=question.difficulty,
            time_taken_seconds=time_taken_seconds,
        )

        return evaluation

    def create_intervention(
        self,
        misconception: MisconceptionRecord,
        current_strategy: TeachingStrategy,
        subject: str = "physics",
    ) -> InterventionPlan:
        return self.intervention_engine.create_intervention_plan(
            misconception=misconception,
            current_strategy=current_strategy,
            subject=subject,
        )

    def _initialize_sample_question_bank(self) -> None:
        """Pre-seeds standard physics, math, programming benchmark questions."""
        q_ohms = Question(
            question_id="q_ohms_1",
            lesson_id="lesson_ohms_law",
            concept="ohms_law",
            type=QuestionType.CONCEPTUAL,
            difficulty=DifficultyLevel.BASIC,
            prompt="What happens to the current (I) in a circuit if resistance (R) increases while voltage (V) remains constant?",
            expected_answer="The current decreases because current and resistance are inversely proportional (I = V / R).",
            rubric=AnswerRubric(
                criteria=["Identifies current decreases", "Mentions inverse relationship or I = V/R"],
                key_terms=["decreases", "decrease", "inversely", "drops", "reduces", "smaller", "half"],
                anti_patterns=["current increases", "increases", "doubles", "more current"],
                formula="I = V / R",
            ),
            misconception_targets=[
                MisconceptionTarget(
                    misconception_type="inverse_relationship_confusion",
                    trigger_patterns=["current increases", "increases", "doubles", "more current", "higher current", "doubled"],
                    explanation="Student believes increasing resistance increases electrical current.",
                    remediation_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                )
            ],
            learning_objective="Master Ohm's law inverse relationship",
            language="en",
            is_checkpoint=True,
        )
        self.store_question(q_ohms)

        q_math = Question(
            question_id="q_math_1",
            lesson_id="lesson_algebra",
            concept="algebra_equations",
            type=QuestionType.PROBLEM_SOLVING,
            difficulty=DifficultyLevel.BASIC,
            prompt="Calculate the value of: 10 + 4 * 2",
            expected_answer="18",
            rubric=AnswerRubric(
                expected_numerical_value=18.0,
                numerical_tolerance=0.0,
            ),
            misconception_targets=[
                MisconceptionTarget(
                    misconception_type="operator_precedence_error",
                    trigger_patterns=["28"],
                    explanation="Student calculated (10 + 4) * 2 = 28 ignoring operator precedence.",
                    remediation_strategy=TeachingStrategy.STEP_BY_STEP,
                )
            ],
            learning_objective="Apply PEMDAS order of operations correctly",
            language="en",
            is_checkpoint=True,
        )
        self.store_question(q_math)

"""
Adaptive Replanner for Module 4: AI Lesson Planner.
Computes targeted segment replacements on misconception diagnoses without full lesson regeneration.
"""

from __future__ import annotations
from typing import Optional

from app.planner.models import LessonPlan, LessonSegment, VisualPlan
from app.learner.models import LearnerCognitiveState
from app.harness.session import TeachingStrategy


class AdaptiveReplanner:
    """
    Computes precise, localized pedagogical adjustments when a student encounters a misconception or failure.
    """

    @classmethod
    def replan_after_evaluation(
        cls,
        current_plan: LessonPlan,
        concept: str,
        is_correct: bool,
        score: float = 1.0,
        misconception_type: Optional[str] = None,
        misconception_belief: Optional[str] = None,
        learner_state: Optional[LearnerCognitiveState] = None,
    ) -> LessonSegment:
        """
        Generates the next pedagogical segment based on student evaluation evidence.
        """
        if is_correct:
            # Advance to the next concept or extension application
            return LessonSegment(
                concept=concept,
                purpose="extension_and_mastery",
                duration_minutes=4.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal=f"Reinforce success and extend {concept} to broader applications.",
                difficulty=min(5, current_plan.difficulty + 1),
                expected_learning_outcome=f"Deepened proficiency in {concept}.",
            )

        if misconception_type:
            # Targeted cognitive remediation
            if "inverse" in misconception_type.lower() or "proportion" in misconception_type.lower():
                strategy = TeachingStrategy.SIMPLE_ANALOGY
                v_type = "analogy_water_circuit"
                goal = f"Clarify inverse relationship in {concept} using hydraulic constriction analogy."
            elif "assignment" in misconception_type.lower() or "equality" in misconception_type.lower():
                strategy = TeachingStrategy.CONTRASTIVE_EXPLANATION
                v_type = "code_block"
                goal = f"Contrast variable assignment ('=') with equality check ('==') in {concept}."
            else:
                strategy = TeachingStrategy.SIMPLE_ANALOGY
                v_type = "analogy_water_circuit"
                goal = f"Remediate diagnosed misconception '{misconception_type}' via concrete analogy."

            remediation_visual = VisualPlan(
                visual_type=v_type,
                purpose=f"Remediation visual for {misconception_type}",
                concept=concept,
                required_elements=["highlight_flaw", "corrected_analogy"],
            )

            return LessonSegment(
                concept=concept,
                purpose="remediation",
                duration_minutes=5.0,
                teaching_strategy=strategy,
                explanation_goal=goal,
                visual_strategy=remediation_visual,
                question_prompt=f"Re-check: When the governing constraint increases in {concept}, what happens to the output?",
                question_type="conceptual",
                difficulty=max(1, current_plan.difficulty - 1),
                expected_learning_outcome=f"Resolve {misconception_type} and re-establish accurate mental model.",
            )

        # Generic wrong answer without diagnosed misconception -> Step-by-step reinforcement
        return LessonSegment(
            concept=concept,
            purpose="reinforcement",
            duration_minutes=4.0,
            teaching_strategy=TeachingStrategy.STEP_BY_STEP,
            explanation_goal=f"Break down {concept} into simpler constituent steps to resolve ambiguity.",
            difficulty=current_plan.difficulty,
            expected_learning_outcome=f"Clarified step-by-step execution for {concept}.",
        )

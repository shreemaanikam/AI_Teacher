"""
Evidence-Based Cognitive Mastery Engine for Module 3.
Calculates continuous Bayesian/evidence-weighted mastery scores (0.0 to 1.0) and knowledge states.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from app.learner.models import KnowledgeState, MasteryUpdateResult


class MasteryUpdateEngine:
    """
    Computes evidence-weighted concept mastery updates and determines categorical KnowledgeState.
    """

    @classmethod
    def compute_mastery_update(
        cls,
        current_mastery: float,
        is_correct: bool,
        difficulty: int = 2,
        score: float = 1.0,
        confidence: float = 0.9,
        has_misconception: bool = False,
        misconception_severity: str = "medium",
        is_recheck_recovery: bool = False,
    ) -> MasteryUpdateResult:
        """
        Calculates new mastery based on student performance evidence.
        """
        prev = max(0.0, min(1.0, current_mastery))

        if is_correct:
            # Scaled gain based on question difficulty (Level 1 to 5)
            difficulty_factor = 0.10 + (difficulty * 0.04)
            if is_recheck_recovery:
                # Strong positive recovery delta when resolving an active misconception
                delta = 0.25 * confidence
                reason = "Recovered understanding after targeted pedagogical intervention."
            else:
                delta = difficulty_factor * score * confidence
                reason = f"Correct answer on difficulty level {difficulty} question."

            new_mastery = min(1.0, prev + delta)
        else:
            if has_misconception:
                severity_penalty = 0.20 if misconception_severity == "high" else 0.12
                delta = -(severity_penalty * confidence)
                reason = f"Diagnosed active conceptual misconception ({misconception_severity} severity)."
            else:
                delta = -(0.08 * (1.0 - score) * confidence)
                reason = "Incorrect or incomplete response."

            new_mastery = max(0.0, prev + delta)

        # Derive KnowledgeState
        new_mastery_round = round(new_mastery, 3)
        if has_misconception and not is_correct:
            state = KnowledgeState.MISCONCEPTION
        elif not is_correct and new_mastery_round < 0.25:
            state = KnowledgeState.STRUGGLING
        elif new_mastery_round >= 0.85:
            state = KnowledgeState.MASTERED
        elif new_mastery_round >= 0.70:
            state = KnowledgeState.DEVELOPING
        elif new_mastery_round >= 0.30:
            state = KnowledgeState.LEARNING
        elif new_mastery_round > 0.0:
            state = KnowledgeState.INTRODUCED
        else:
            state = KnowledgeState.UNKNOWN

        return MasteryUpdateResult(
            concept="",
            previous_mastery=round(prev, 3),
            new_mastery=new_mastery_round,
            knowledge_state=state,
            delta=round(new_mastery - prev, 3),
            reason=reason,
            confidence=confidence,
        )

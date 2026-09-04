"""
Persistent Learner Cognitive Service for Module 3.
Manages student knowledge profiles, misconception memories, strategy history, and language-independent state.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from app.learner.models import (
    LearnerCognitiveState,
    KnowledgeState,
    MisconceptionMemory,
    StrategyEffectivenessRecord,
    AnswerAttemptLog,
    MasteryUpdateResult,
)
from app.learner.mastery_engine import MasteryUpdateEngine
from app.harness.session import TeachingStrategy


class LearnerCognitiveService:
    """
    Central service maintaining persistent learner states and tracking cognitive progress.
    """

    def __init__(self):
        self._learners: Dict[str, LearnerCognitiveState] = {}

    def get_or_create_learner(
        self,
        learner_id: str,
        display_name: str = "Learner",
        language: str = "en",
        educational_level: str = "beginner",
    ) -> LearnerCognitiveState:
        """Retrieves an existing learner profile or initializes a fresh cognitive state."""
        if learner_id not in self._learners:
            self._learners[learner_id] = LearnerCognitiveState(
                learner_id=learner_id,
                display_name=display_name,
                language=language,
                educational_level=educational_level,
            )
        return self._learners[learner_id]

    def update_from_answer(
        self,
        learner_id: str,
        concept: str,
        is_correct: bool,
        difficulty: int = 2,
        score: float = 1.0,
        confidence: float = 0.9,
        misconception_type: Optional[str] = None,
        misconception_severity: str = "medium",
        question_id: str = "q_default",
        student_answer: str = "",
        active_strategy: Optional[TeachingStrategy] = None,
    ) -> MasteryUpdateResult:
        """
        Updates student mastery and misconception records upon receiving question evaluation evidence.
        """
        learner = self.get_or_create_learner(learner_id)
        prev_mastery = learner.concept_mastery.get(concept, 0.30)

        # Check if this concept had an active misconception being remediated
        active_misc_record = None
        for m in learner.misconceptions:
            if m.concept == concept and not m.resolved:
                active_misc_record = m
                break

        is_recovery = is_correct and (active_misc_record is not None)

        update_res = MasteryUpdateEngine.compute_mastery_update(
            current_mastery=prev_mastery,
            is_correct=is_correct,
            difficulty=difficulty,
            score=score,
            confidence=confidence,
            has_misconception=bool(misconception_type),
            misconception_severity=misconception_severity,
            is_recheck_recovery=is_recovery,
        )
        update_res.concept = concept

        # Apply updates to cognitive profile
        learner.concept_mastery[concept] = update_res.new_mastery
        learner.knowledge_states[concept] = update_res.knowledge_state
        learner.current_concept = concept
        learner.current_mastery = update_res.new_mastery
        learner.updated_at = datetime.now(timezone.utc)

        # Update Misconception Memory
        if misconception_type and not is_correct:
            found = False
            for m in learner.misconceptions:
                if m.misconception_type == misconception_type and m.concept == concept:
                    m.frequency += 1
                    m.last_detected = datetime.now(timezone.utc)
                    m.resolved = False
                    found = True
                    break
            if not found:
                learner.misconceptions.append(
                    MisconceptionMemory(
                        misconception_type=misconception_type,
                        concept=concept,
                        severity=misconception_severity,
                        resolved=False,
                    )
                )
        elif is_recovery and active_misc_record:
            active_misc_record.resolved = True
            active_misc_record.recovery_evidence = f"Passed checkpoint question with score {score}."
            if active_strategy:
                active_misc_record.remediation_used = active_strategy.value

        # Track Strategy Effectiveness
        if active_strategy:
            is_eff = update_res.new_mastery > prev_mastery
            learner.strategy_history.append(
                StrategyEffectivenessRecord(
                    concept=concept,
                    strategy=active_strategy,
                    before_mastery=prev_mastery,
                    after_mastery=update_res.new_mastery,
                    is_effective=is_eff,
                )
            )

        # Log answer attempt
        learner.recent_answers.append(
            AnswerAttemptLog(
                question_id=question_id,
                concept=concept,
                difficulty=difficulty,
                student_answer=student_answer,
                is_correct=is_correct,
                score=score,
                misconception_diagnosed=misconception_type,
            )
        )

        # Update strengths and weak concepts
        self._refresh_strengths_and_weaknesses(learner)
        return update_res

    def _refresh_strengths_and_weaknesses(self, learner: LearnerCognitiveState) -> None:
        strengths = []
        weak = []
        for concept, score in learner.concept_mastery.items():
            if score >= 0.70:
                strengths.append(concept)
            elif score < 0.40:
                weak.append(concept)
        learner.strengths = strengths
        learner.weak_concepts = weak


# Global singleton instance
_GLOBAL_LEARNER_SERVICE = LearnerCognitiveService()


def get_learner_service() -> LearnerCognitiveService:
    return _GLOBAL_LEARNER_SERVICE

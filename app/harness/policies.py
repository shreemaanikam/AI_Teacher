"""
Centralized Policy Engine for Module 5 (Teaching Harness).
Deterministic rules governing teaching adaptations, strategy switching, and difficulty scaling.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingDecision,
    TeachingSessionState,
    ActiveMisconception,
    ConceptMasterySnapshot,
)


class PolicyConfig(BaseModel):
    """Configurable thresholds for teaching policies."""
    mastery_advance_threshold: float = 0.70
    mastery_reexplain_threshold: float = 0.40
    mastery_increase_step: float = 0.25
    mastery_decrease_step: float = 0.15
    max_consecutive_failures_before_prerequisite: int = 2
    success_streak_for_difficulty_increase: int = 2
    failure_streak_for_difficulty_decrease: int = 2
    evidence_confidence_threshold: float = 0.65


# Strategy escalation sequence when student struggles repeatedly
STRATEGY_FALLBACK_ORDER: List[TeachingStrategy] = [
    TeachingStrategy.DIRECT_EXPLANATION,
    TeachingStrategy.SIMPLE_ANALOGY,
    TeachingStrategy.VISUAL_EXPLANATION,
    TeachingStrategy.STEP_BY_STEP,
    TeachingStrategy.EXAMPLE_FIRST,
    TeachingStrategy.CONTRASTIVE_EXPLANATION,
    TeachingStrategy.PREREQUISITE_REVIEW,
]


class TeachingPolicyEngine:
    """
    Evaluates learner outcomes deterministically against configurable policies.
    Selects the next teaching state, action, strategy, visual mode, and difficulty.
    """

    def __init__(self, config: PolicyConfig | None = None):
        self.config = config or PolicyConfig()

    def select_next_strategy(
        self,
        current_strategy: TeachingStrategy,
        consecutive_failures: int,
        misconception: Optional[ActiveMisconception] = None,
    ) -> TeachingStrategy:
        """Determines the next explanation strategy ensuring meaningful pedagogical variation."""
        if consecutive_failures >= self.config.max_consecutive_failures_before_prerequisite:
            return TeachingStrategy.PREREQUISITE_REVIEW

        if misconception:
            # Misconceptions benefit primarily from analogies, visual models, or contrastive comparisons
            if current_strategy == TeachingStrategy.DIRECT_EXPLANATION:
                return TeachingStrategy.SIMPLE_ANALOGY
            elif current_strategy == TeachingStrategy.SIMPLE_ANALOGY:
                return TeachingStrategy.VISUAL_EXPLANATION
            elif current_strategy == TeachingStrategy.VISUAL_EXPLANATION:
                return TeachingStrategy.CONTRASTIVE_EXPLANATION
            else:
                return TeachingStrategy.STEP_BY_STEP

        # Standard rotation
        try:
            current_idx = STRATEGY_FALLBACK_ORDER.index(current_strategy)
            next_idx = (current_idx + 1) % len(STRATEGY_FALLBACK_ORDER)
            return STRATEGY_FALLBACK_ORDER[next_idx]
        except ValueError:
            return TeachingStrategy.SIMPLE_ANALOGY

    def select_visual_strategy(
        self,
        subject: str,
        concept: str,
        strategy: TeachingStrategy,
        misconception: Optional[ActiveMisconception] = None,
    ) -> str:
        """Selects the visual representation based on subject, concept, and pedagogical goal."""
        subject_lower = subject.lower()

        if "physics" in subject_lower:
            if misconception and "inverse" in misconception.misconception_type.lower():
                return "analogy_water_circuit"
            elif strategy == TeachingStrategy.SIMPLE_ANALOGY:
                return "analogy_diagram"
            elif strategy == TeachingStrategy.VISUAL_EXPLANATION:
                return "circuit_diagram_with_meters"
            return "circuit_diagram"
        elif "math" in subject_lower:
            if strategy in (TeachingStrategy.STEP_BY_STEP, TeachingStrategy.EXAMPLE_FIRST):
                return "step_by_step_calculation"
            return "function_graph_and_equation"
        elif "program" in subject_lower:
            return "code_execution_flow"
        elif "bio" in subject_lower:
            return "labeled_anatomy_process"
        elif "chem" in subject_lower:
            return "molecular_reaction_diagram"
        return "structured_concept_diagram"

    def evaluate_checkpoint_response(
        self,
        session: TeachingSessionState,
        is_correct: bool,
        score: float,
        confidence: float,
        misconception: Optional[ActiveMisconception] = None,
        evaluator_reason: str = "",
    ) -> TeachingDecision:
        """
        Main policy decision point following an answer evaluation.
        Produces a validated TeachingDecision.
        """
        current_concept = session.current_concept
        current_mastery = session.concept_mastery.get(current_concept, 0.5)

        # Update mastery snapshot
        snapshot = session.concept_snapshots.get(
            current_concept,
            ConceptMasterySnapshot(concept=current_concept, mastery=current_mastery),
        )
        snapshot.attempts += 1

        if is_correct:
            snapshot.correct_count += 1
            new_mastery = min(1.0, current_mastery + self.config.mastery_increase_step * score)
            session.concept_mastery[current_concept] = round(new_mastery, 3)
            snapshot.mastery = session.concept_mastery[current_concept]
            snapshot.confidence = max(snapshot.confidence, confidence)
            session.concept_snapshots[current_concept] = snapshot

            session.consecutive_successes += 1
            session.consecutive_failures = 0

            # Mark active misconceptions as resolved if applicable
            for m in session.active_misconceptions:
                if m.concept == current_concept:
                    m.resolved = True
                    session.resolved_misconceptions.append(m)
            session.active_misconceptions = [m for m in session.active_misconceptions if not m.resolved]

            # Adjust difficulty upwards if consistent success
            if (
                session.consecutive_successes >= self.config.success_streak_for_difficulty_increase
                and session.current_difficulty.value < DifficultyLevel.ADVANCED.value
            ):
                session.current_difficulty = DifficultyLevel(session.current_difficulty.value + 1)

            # Check if all concepts are completed
            is_last_concept = session.current_concept_index >= len(session.concepts_list) - 1
            if is_last_concept and new_mastery >= self.config.mastery_advance_threshold:
                return TeachingDecision(
                    current_state=SessionState.EVALUATE,
                    action=ActionType.RUN_ASSESSMENT,
                    reason=f"Concept '{current_concept}' mastered (mastery={new_mastery:.2f}). Proceeding to final assessment.",
                    concept=current_concept,
                    difficulty=session.current_difficulty,
                    teaching_strategy=TeachingStrategy.SUMMARY_RECAP,
                    visual_strategy="assessment_overview",
                    language=session.language,
                    next_state=SessionState.ASSESSMENT,
                    requires_video=False,
                    requires_question=True,
                    confidence=confidence,
                )
            else:
                # Advance to next concept
                next_idx = session.current_concept_index + 1
                next_concept = (
                    session.concepts_list[next_idx]
                    if next_idx < len(session.concepts_list)
                    else current_concept
                )
                session.current_concept_index = min(next_idx, max(0, len(session.concepts_list) - 1))
                session.current_concept = next_concept

                return TeachingDecision(
                    current_state=SessionState.EVALUATE,
                    action=ActionType.ADVANCE_CONCEPT,
                    reason=f"Correct answer received (score={score:.2f}). Advancing to concept '{next_concept}'.",
                    concept=next_concept,
                    difficulty=session.current_difficulty,
                    teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                    visual_strategy=self.select_visual_strategy(session.subject, next_concept, TeachingStrategy.DIRECT_EXPLANATION),
                    language=session.language,
                    next_state=SessionState.TEACH,
                    requires_video=True,
                    requires_question=False,
                    confidence=confidence,
                )

        else:
            # Incorrect or Misconception detected
            new_mastery = max(0.0, current_mastery - self.config.mastery_decrease_step)
            session.concept_mastery[current_concept] = round(new_mastery, 3)
            snapshot.mastery = session.concept_mastery[current_concept]
            session.concept_snapshots[current_concept] = snapshot

            session.consecutive_failures += 1
            session.consecutive_successes = 0

            # Adjust difficulty downwards if repeating errors
            if (
                session.consecutive_failures >= self.config.failure_streak_for_difficulty_decrease
                and session.current_difficulty.value > DifficultyLevel.FOUNDATION.value
            ):
                session.current_difficulty = DifficultyLevel(session.current_difficulty.value - 1)

            if misconception:
                session.active_misconceptions.append(misconception)

            # Determine next teaching strategy
            new_strategy = self.select_next_strategy(
                session.current_strategy,
                session.consecutive_failures,
                misconception,
            )
            session.strategy_history.append(session.current_strategy)
            session.current_strategy = new_strategy

            visual_strat = self.select_visual_strategy(
                session.subject, current_concept, new_strategy, misconception
            )

            reason = (
                f"Misconception '{misconception.misconception_type}' detected: {misconception.belief}. "
                f"Switching strategy from {session.strategy_history[-1].value} to {new_strategy.value}."
                if misconception
                else f"Incorrect response (score={score:.2f}). Retrying concept with {new_strategy.value} strategy."
            )

            return TeachingDecision(
                current_state=SessionState.EVALUATE,
                action=ActionType.ADAPT_STRATEGY,
                reason=reason,
                concept=current_concept,
                difficulty=session.current_difficulty,
                teaching_strategy=new_strategy,
                visual_strategy=visual_strat,
                language=session.language,
                next_state=SessionState.ADAPT,
                requires_video=True,
                requires_question=True,
                confidence=confidence,
                metadata={
                    "misconception": misconception.model_dump() if misconception else None,
                    "evaluator_reason": evaluator_reason,
                    "previous_strategy": session.strategy_history[-1].value,
                    "new_strategy": new_strategy.value,
                },
            )

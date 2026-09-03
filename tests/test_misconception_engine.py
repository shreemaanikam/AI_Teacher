"""
Unit Tests for Misconception Taxonomy, Intervention Generation, and Adaptive Difficulty.
"""

from app.assessment.taxonomy import MisconceptionTaxonomy, MisconceptionDefinition
from app.assessment.interventions import InterventionEngine
from app.assessment.models import MisconceptionRecord
from app.assessment.difficulty import AdaptiveDifficultyController
from app.harness.session import DifficultyLevel, TeachingStrategy


def test_taxonomy_registration_and_lookup():
    taxonomy = MisconceptionTaxonomy()
    results = taxonomy.find_misconceptions("physics", "ohms_law")
    assert len(results) >= 2
    types = [r.misconception_type for r in results]
    assert "inverse_relationship_confusion" in types
    assert "voltage_current_confusion" in types


def test_intervention_strategy_switching():
    engine = InterventionEngine()
    record = MisconceptionRecord(
        concept="ohms_law",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="current will increase",
        confidence=0.9,
    )

    plan1 = engine.create_intervention_plan(record, TeachingStrategy.DIRECT_EXPLANATION)
    assert plan1.previous_strategy == TeachingStrategy.DIRECT_EXPLANATION
    assert plan1.new_strategy == TeachingStrategy.SIMPLE_ANALOGY

    plan2 = engine.create_intervention_plan(record, TeachingStrategy.SIMPLE_ANALOGY)
    assert plan2.new_strategy == TeachingStrategy.VISUAL_EXPLANATION


def test_adaptive_difficulty_scaling():
    ctrl = AdaptiveDifficultyController(window_size=3)

    # 1. 3 consecutive strong successes should promote difficulty
    ctrl.record_attempt(is_correct=True, score=1.0, confidence=0.95, has_misconception=False, difficulty_level=DifficultyLevel.BASIC)
    ctrl.record_attempt(is_correct=True, score=1.0, confidence=0.95, has_misconception=False, difficulty_level=DifficultyLevel.BASIC)
    ctrl.record_attempt(is_correct=True, score=1.0, confidence=0.95, has_misconception=False, difficulty_level=DifficultyLevel.BASIC)

    promoted = ctrl.compute_next_difficulty(DifficultyLevel.BASIC, current_mastery=0.85)
    assert promoted == DifficultyLevel.INTERMEDIATE

    # 2. Repeated misconceptions should demote difficulty
    ctrl.record_attempt(is_correct=False, score=0.1, confidence=0.9, has_misconception=True, difficulty_level=DifficultyLevel.INTERMEDIATE)
    ctrl.record_attempt(is_correct=False, score=0.1, confidence=0.9, has_misconception=True, difficulty_level=DifficultyLevel.INTERMEDIATE)

    demoted = ctrl.compute_next_difficulty(DifficultyLevel.INTERMEDIATE, current_mastery=0.4)
    assert demoted == DifficultyLevel.BASIC

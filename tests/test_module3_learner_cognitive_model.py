"""
Tests for Module 3: Learner Cognitive Model.
Verifies dynamic Bayesian mastery updates, knowledge state transitions, misconception memory, strategy tracking, and language-independence.
"""

import pytest
from app import create_app
from app.learner.models import KnowledgeState
from app.learner.mastery_engine import MasteryUpdateEngine
from app.learner.cognitive_service import LearnerCognitiveService
from app.harness.session import TeachingStrategy


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_student_a_correct_answer_advances_mastery():
    svc = LearnerCognitiveService()
    # Student A starts at baseline 0.30
    res = svc.update_from_answer(
        learner_id="student_a",
        concept="ohms_law",
        is_correct=True,
        difficulty=3,
        score=1.0,
        confidence=0.95,
    )
    assert res.new_mastery > 0.30
    assert res.knowledge_state in [KnowledgeState.LEARNING, KnowledgeState.DEVELOPING]
    assert res.delta > 0


def test_2_student_b_misconception_decreases_mastery():
    svc = LearnerCognitiveService()
    # Student B diagnosed with inverse proportion confusion
    res = svc.update_from_answer(
        learner_id="student_b",
        concept="ohms_law",
        is_correct=False,
        difficulty=2,
        score=0.0,
        confidence=0.90,
        misconception_type="inverse_relationship_confusion",
        misconception_severity="high",
    )
    assert res.new_mastery < 0.30
    assert res.knowledge_state == KnowledgeState.MISCONCEPTION

    learner = svc.get_or_create_learner("student_b")
    assert len(learner.misconceptions) == 1
    assert learner.misconceptions[0].misconception_type == "inverse_relationship_confusion"
    assert learner.misconceptions[0].resolved is False


def test_3_student_b_remediation_recovery_resolves_misconception():
    svc = LearnerCognitiveService()
    # 1. Initial misconception
    svc.update_from_answer(
        learner_id="student_b_rec",
        concept="ohms_law",
        is_correct=False,
        misconception_type="inverse_relationship_confusion",
        misconception_severity="high",
    )

    # 2. Re-check correct response after SIMPLE_ANALOGY
    rec_res = svc.update_from_answer(
        learner_id="student_b_rec",
        concept="ohms_law",
        is_correct=True,
        difficulty=2,
        score=1.0,
        active_strategy=TeachingStrategy.SIMPLE_ANALOGY,
    )

    assert rec_res.new_mastery > 0.30
    learner = svc.get_or_create_learner("student_b_rec")
    assert learner.misconceptions[0].resolved is True
    assert learner.misconceptions[0].remediation_used == "SIMPLE_ANALOGY"
    assert len(learner.strategy_history) == 1
    assert learner.strategy_history[0].is_effective is True


def test_4_repeated_misconception_increments_frequency():
    svc = LearnerCognitiveService()
    for _ in range(3):
        svc.update_from_answer(
            learner_id="student_struggling",
            concept="variable_scope",
            is_correct=False,
            misconception_type="variable_shadowing_confusion",
            misconception_severity="medium",
        )

    learner = svc.get_or_create_learner("student_struggling")
    assert len(learner.misconceptions) == 1
    assert learner.misconceptions[0].frequency == 3
    assert "variable_scope" in learner.weak_concepts


def test_5_language_independence_preserves_cognitive_state():
    svc = LearnerCognitiveService()
    learner = svc.get_or_create_learner("student_multi", language="en")
    svc.update_from_answer(
        learner_id="student_multi",
        concept="newtons_second_law",
        is_correct=True,
        difficulty=3,
        score=1.0,
    )

    initial_mastery = learner.concept_mastery["newtons_second_law"]

    # Student switches presentation language to Hindi and then Tamil
    learner.language = "hi"
    assert learner.concept_mastery["newtons_second_law"] == initial_mastery

    learner.language = "ta"
    assert learner.concept_mastery["newtons_second_law"] == initial_mastery


def test_6_rest_api_learner_endpoints(client):
    # 1. Update mastery via REST
    update_res = client.post(
        "/api/v1/learners/student_rest_01/mastery/update",
        json={
            "concept": "cellular_respiration",
            "is_correct": True,
            "difficulty": 3,
            "score": 1.0,
        },
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["success"] is True

    # 2. Get concepts
    get_res = client.get("/api/v1/learners/student_rest_01/concepts")
    assert get_res.status_code == 200
    payload = get_res.get_json()
    assert "cellular_respiration" in payload["concept_mastery"]
    assert payload["concept_mastery"]["cellular_respiration"] > 0.30

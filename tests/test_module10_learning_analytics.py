"""
Tests for Module 10: Learning Analytics & Recommendation Engine.
Verifies event logging, progress calculation, misconception trends, revision scheduling, and prerequisite learning paths.
"""

import pytest
from app import create_app
from app.analytics.models import LearningEventType, MasteryTrend
from app.analytics.event_logger import get_event_logger
from app.analytics.analytics_engine import LearningAnalyticsEngine
from app.analytics.recommendations import RevisionRecommendationEngine
from app.analytics.learning_path import LearningPathEngine
from app.learner.cognitive_service import get_learner_service


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_event_logging_and_progress_analytics():
    event_logger = get_event_logger()
    event_logger.log_event(
        learner_id="student_ana_01",
        concept_id="ohms_law",
        event_type=LearningEventType.QUESTION_ANSWERED,
        score=1.0,
        duration_seconds=45.0,
    )

    stats = LearningAnalyticsEngine.compute_learner_analytics("student_ana_01")
    assert stats["total_questions_attempted"] >= 1
    assert stats["question_accuracy_rate"] >= 0.70
    assert stats["estimated_study_time_minutes"] > 0


def test_2_concept_breakdown_and_trends():
    learner_svc = get_learner_service()
    learner = learner_svc.get_or_create_learner("student_ana_02")
    learner.concept_mastery["ohms_law"] = 0.88
    learner.concept_mastery["resistors_in_parallel"] = 0.32

    breakdown = LearningAnalyticsEngine.get_concept_breakdown("student_ana_02")
    assert len(breakdown) == 2
    ohms = next(c for c in breakdown if c.concept == "ohms_law")
    assert ohms.trend == MasteryTrend.IMPROVING
    parallel = next(c for c in breakdown if c.concept == "resistors_in_parallel")
    assert parallel.trend == MasteryTrend.DECLINING


def test_3_revision_recommendation_prioritizes_misconceptions():
    learner_svc = get_learner_service()
    # Student with repeated misconception
    learner_svc.update_from_answer(
        learner_id="student_rev_01",
        concept="ohms_law",
        is_correct=False,
        misconception_type="inverse_relationship_confusion",
    )
    learner_svc.update_from_answer(
        learner_id="student_rev_01",
        concept="ohms_law",
        is_correct=False,
        misconception_type="inverse_relationship_confusion",
    )

    recs = RevisionRecommendationEngine.generate_recommendations("student_rev_01")
    assert len(recs) >= 1
    assert recs[0].priority == "HIGH"
    assert "inverse_relationship_confusion" in recs[0].reason


def test_4_prerequisite_learning_path_gates_advanced_topics():
    learner_svc = get_learner_service()
    learner = learner_svc.get_or_create_learner("student_path_01")

    # Student has zero mastery in voltage_current_basics
    path = LearningPathEngine.compute_learning_path("student_path_01", subject="physics")
    # ohms_law and subsequent concepts should be blocked or not recommended until voltage_current_basics is mastered
    assert "kirchhoffs_laws" in path.blocked_topics

    # Student masters prerequisite
    learner.concept_mastery["electric_charge_basics"] = 0.90
    learner.concept_mastery["voltage_current_basics"] = 0.85
    updated_path = LearningPathEngine.compute_learning_path("student_path_01", subject="physics")
    assert "ohms_law" in updated_path.next_topics


def test_5_rest_api_analytics_endpoints(client):
    # 1. Overview
    res = client.get("/api/v1/analytics/student_ana_01")
    assert res.status_code == 200
    assert res.get_json()["success"] is True

    # 2. Learning path
    res_path = client.get("/api/v1/analytics/student_ana_01/learning-path?subject=physics")
    assert res_path.status_code == 200
    assert "current_topic" in res_path.get_json()["learning_path"]

    # 3. Recommendations
    res_rec = client.post("/api/v1/recommendations/generate", json={"learner_id": "student_ana_01"})
    assert res_rec.status_code == 200
    assert "recommendations" in res_rec.get_json()

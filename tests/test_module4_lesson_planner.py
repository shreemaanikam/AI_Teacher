"""
Tests for Module 4: AI Lesson Planner.
Verifies time budgeting (5/20/60 min), level adaptation, subject profiles, RAG grounding, and adaptive replanning.
"""

import pytest
from app import create_app
from app.planner.models import (
    LessonPlannerInput,
    LessonPlan,
    LearningObjectiveType,
    LessonSegment,
)
from app.planner.engine import LessonPlannerEngine
from app.planner.replanner import AdaptiveReplanner
from app.input.models import TeachingRequest, LearnerLevel, TimeBudget, TeachingStyle
from app.rag.models import EvidencePackage, EvidenceItem, GroundingLevel
from app.harness.session import TeachingStrategy


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _create_mock_input(
    topic: str = "Ohm's Law",
    subject: str = "physics",
    time_minutes: int = 20,
    level: LearnerLevel = LearnerLevel.BEGINNER,
    objective: LearningObjectiveType = LearningObjectiveType.UNDERSTAND,
    grounding: GroundingLevel = GroundingLevel.SUPPORTED,
) -> LessonPlannerInput:
    req = TeachingRequest(
        learner_id="learner_test",
        source_type="direct_topic",
        topic=topic,
        subject=subject,
        requested_language="en",
        learner_level=level,
        available_time=TimeBudget.TWENTY_MIN if time_minutes == 20 else (TimeBudget.FIVE_MIN if time_minutes == 5 else TimeBudget.SIXTY_MIN),
        time_minutes=time_minutes,
        teaching_style=TeachingStyle.SIMPLE,
    )
    evidence = EvidencePackage(
        query=topic,
        target_concept=topic,
        grounding_level=grounding,
        evidence_items=[
            EvidenceItem(chunk_id="chk_01", document_id="doc_01", excerpt=f"Definition of {topic}", page=1)
        ] if grounding != GroundingLevel.UNSUPPORTED else [],
        combined_context=f"Evidence for {topic}" if grounding != GroundingLevel.UNSUPPORTED else "Insufficient evidence.",
    )
    return LessonPlannerInput(
        teaching_request=req,
        evidence_package=evidence,
        available_time=req.available_time,
        time_minutes=time_minutes,
        learning_objective=objective,
        educational_level=level,
        teaching_style=TeachingStyle.SIMPLE,
        language="en",
        subject=subject,
    )


def test_1_five_minute_sprint_plan():
    inp = _create_mock_input(topic="Ohm's Law", time_minutes=5)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.estimated_duration_minutes == 5
    assert len(plan.segments) == 2
    total_time = sum(s.duration_minutes for s in plan.segments)
    assert total_time == 5.0
    assert len(plan.assessment_points) == 1


def test_2_twenty_minute_standard_plan():
    inp = _create_mock_input(topic="Ohm's Law", time_minutes=20)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.estimated_duration_minutes == 20
    assert len(plan.segments) == 5
    assert len(plan.visual_plan) >= 1
    assert len(plan.assessment_points) >= 1


def test_3_sixty_minute_deep_dive_plan():
    inp = _create_mock_input(topic="Ohm's Law", time_minutes=60, level=LearnerLevel.ADVANCED)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.estimated_duration_minutes == 60
    assert len(plan.segments) == 6
    assert plan.difficulty == 4
    assert len(plan.visual_plan) >= 2


def test_4_subject_aware_programming_plan():
    inp = _create_mock_input(topic="Python Conditionals", subject="programming", time_minutes=20)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.subject == "programming"
    visual_types = [v.visual_type for v in plan.visual_plan]
    assert "code_block" in visual_types


def test_5_subject_aware_mathematics_plan():
    inp = _create_mock_input(topic="Linear Equations", subject="mathematics", time_minutes=20)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.subject == "mathematics"
    visual_types = [v.visual_type for v in plan.visual_plan]
    assert "plot_curve" in visual_types


def test_6_unsupported_rag_sets_knowledge_confidence_low():
    inp = _create_mock_input(topic="Obscure Concept", time_minutes=20, grounding=GroundingLevel.UNSUPPORTED)
    plan = LessonPlannerEngine.generate_plan(inp)
    assert plan.is_grounded is False
    assert plan.segments[0].knowledge_confidence == "LOW"


def test_7_adaptive_replanning_on_misconception():
    inp = _create_mock_input(topic="Ohm's Law", time_minutes=20)
    plan = LessonPlannerEngine.generate_plan(inp)

    # Student triggers inverse proportion confusion
    replacement = AdaptiveReplanner.replan_after_evaluation(
        current_plan=plan,
        concept="Ohm's Law",
        is_correct=False,
        score=0.0,
        misconception_type="inverse_relationship_confusion",
    )

    assert replacement.purpose == "remediation"
    assert replacement.teaching_strategy == TeachingStrategy.SIMPLE_ANALOGY
    assert replacement.visual_strategy is not None
    assert replacement.visual_strategy.visual_type == "analogy_water_circuit"


def test_8_rest_api_generate_and_replan(client):
    # 1. Generate plan via API
    res = client.post(
        "/api/v1/planner/generate",
        json={"topic": "Ohm's Law", "subject": "physics", "time_budget": "20_MIN"},
    )
    assert res.status_code == 201
    plan_data = res.get_json()["lesson_plan"]
    assert plan_data["title"] == "Adaptive Lesson: Ohm's Law"
    lesson_id = plan_data["lesson_id"]

    # 2. Replan segment via API
    replan_res = client.post(
        "/api/v1/planner/replan",
        json={
            "lesson_id": lesson_id,
            "concept": "Ohm's Law",
            "is_correct": False,
            "misconception_type": "inverse_relationship_confusion",
        },
    )
    assert replan_res.status_code == 200
    rep_seg = replan_res.get_json()["replacement_segment"]
    assert rep_seg["purpose"] == "remediation"

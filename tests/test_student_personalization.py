"""
Tests for Phase 4: Student Profile & Personalization.
Verifies persistence in learner_profiles, retrieval of college/exam parameters,
and automatic personalization of the Teaching Harness (strategy, difficulty, weak concept prioritization).
"""

import pytest
from app import create_app
from app.db.repository import get_teaching_repository
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import TeachingStrategy, DifficultyLevel


@pytest.fixture
def app_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_student_profile_persistence_and_retrieval():
    """Verify storing and retrieving rich college student profiles in database."""
    repo = get_teaching_repository()

    profile_data = {
        "student_id": "student_rahul_gate2026",
        "display_name": "Rahul Sharma",
        "college_grade": "B.Tech Computer Science 3rd Year (IIT Delhi)",
        "target_exam": "GATE CS 2026",
        "exam_date": "2026-09-08",
        "target_score": "90%",
        "learning_speed": "fast",
        "preferred_teaching_style": "FORMAL_RIGOROUS",
        "weak_concepts": ["Recursion", "Dynamic Programming"],
        "strengths": ["Array Data Structures", "Bit Manipulation"],
        "study_history": {
            "topics_covered": ["Linear Search", "Binary Search"],
            "hours_spent": 14.5,
            "questions_attempted": 42,
            "questions_correct": 36,
        },
    }

    saved = repo.save_learner_profile(profile_data)
    assert saved["id"] == "student_rahul_gate2026"
    assert saved["college_grade"] == "B.Tech Computer Science 3rd Year (IIT Delhi)"
    assert saved["target_exam"] == "GATE CS 2026"
    assert saved["target_score"] == "90%"
    assert saved["preferred_teaching_style"] == "FORMAL_RIGOROUS"
    assert "Recursion" in saved["weak_concepts"]

    # Re-fetch from repository
    fetched = repo.get_learner_profile("student_rahul_gate2026")
    assert fetched is not None
    assert fetched["display_name"] == "Rahul Sharma"
    assert fetched["learning_speed"] == "fast"
    assert fetched["study_history"]["hours_spent"] == 14.5


def test_teaching_harness_personalization_from_profile():
    """
    Verification test:
    1. Create profile: 'Exam in 3 days, target 90%, needs formal style, weak in recursion'
    2. Start a session with topic covering Algorithms (including Recursion)
    3. Verify Teaching Harness adapts strategy, difficulty, and concept order based on profile.
    """
    repo = get_teaching_repository()
    student_id = "student_personalization_test"
    repo.save_learner_profile({
        "student_id": student_id,
        "display_name": "Aakash Verma",
        "college_grade": "2nd Year Engineering",
        "target_exam": "End-Semester Exam in 3 days",
        "exam_date": "2026-09-07",
        "target_score": "92%",
        "learning_speed": "moderate",
        "preferred_teaching_style": "FORMAL_RIGOROUS",
        "weak_concepts": ["Recursion"],
    })

    orchestrator = MasterTeachingOrchestrator(repository=repo)
    session = orchestrator.start_session(
        student_id=student_id,
        lesson_id="lesson_algo_01",
        topic="Algorithmic Problem Solving",
        subject="Computer Science",
        concepts_list=["Algorithm Complexity", "Recursion", "Iterative Loops"],
    )

    # 1. Verify formal style mapped to rigorous step-by-step strategy
    assert session.current_strategy == TeachingStrategy.STEP_BY_STEP

    # 2. Verify target 92% elevated initial difficulty to INTERMEDIATE
    assert session.current_difficulty == DifficultyLevel.INTERMEDIATE

    # 3. Verify weak concept 'Recursion' was prioritized to the front of the curriculum
    assert session.concepts_list[0] == "Recursion"
    assert session.current_concept == "Recursion"

    # 4. Verify weak concept has lower initial mastery and active misconception registered
    assert session.concept_mastery["Recursion"] < 0.30
    assert len(session.active_misconceptions) >= 1
    assert "Recursion" in session.active_misconceptions[0].misconception_type

    # 5. Verify student profile attached to metadata
    assert "student_profile" in session.metadata
    assert session.metadata["student_profile"]["target_score"] == "92%"


def test_api_learner_profile_endpoints(app_client):
    """Test REST API routes for saving and retrieving student profile."""
    profile_payload = {
        "student_id": "student_priya_e2e",
        "display_name": "Priya Patel",
        "college_grade": "B.Sc Physics 2nd Year",
        "target_exam": "University Midterms",
        "target_score": "88%",
        "preferred_teaching_style": "ANALOGY_HEAVY",
        "weak_concepts": ["Electromagnetic Waves"],
    }

    # 1. POST /api/v1/learners/profile
    resp = app_client.post("/api/v1/learners/profile", json=profile_payload)
    assert resp.status_code == 200
    res_data = resp.get_json()
    assert res_data["success"] is True
    assert res_data["profile"]["preferred_teaching_style"] == "ANALOGY_HEAVY"

    # 2. GET /api/v1/learners/<learner_id>/profile
    resp_get = app_client.get("/api/v1/learners/student_priya_e2e/profile")
    assert resp_get.status_code == 200
    get_data = resp_get.get_json()
    assert get_data["success"] is True
    assert get_data["profile"]["display_name"] == "Priya Patel"
    assert get_data["profile"]["college_grade"] == "B.Sc Physics 2nd Year"

    # 3. Verify Harness adapts to ANALOGY_HEAVY for Priya
    orchestrator = MasterTeachingOrchestrator()
    session = orchestrator.start_session(
        student_id="student_priya_e2e",
        lesson_id="lesson_optics_01",
        topic="Wave Optics",
        subject="Physics",
    )
    assert session.current_strategy == TeachingStrategy.SIMPLE_ANALOGY

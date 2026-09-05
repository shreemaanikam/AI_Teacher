"""
Tests for Phase 9A: Student Account & Identity.
Verifies real collegiate student identity records, multi-student support,
database persistence, field tracking, and REST endpoints.
"""

import pytest
from app import create_app
from app.learner.models import StudentProfile
from app.db.repository import get_teaching_repository


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_student_profile_model_defaults():
    """Verify StudentProfile Pydantic model defaults and fields."""
    student = StudentProfile(
        name="Rohan Verma",
        college="IIT Madras",
        department="Computer Science and Engineering",
        degree="B.Tech",
        year=3,
        semester=5,
        preferred_language="en",
        learning_style="VISUAL_AND_ANALOGIES",
        target_score="95%",
        available_study_hours=18.0,
        exam_dates={"Data Structures": "2026-10-15", "Algorithms": "2026-10-22"},
    )
    assert student.student_id.startswith("std_")
    assert student.name == "Rohan Verma"
    assert student.college == "IIT Madras"
    assert student.department == "Computer Science and Engineering"
    assert student.year == 3
    assert student.semester == 5
    assert student.available_study_hours == 18.0
    assert "Data Structures" in student.exam_dates


def test_multi_student_creation_and_persistence(client):
    """Verify multiple distinct student profiles persist without collision."""
    repo = get_teaching_repository()

    student_a_data = {
        "student_id": "std_test_rohan_9a",
        "name": "Rohan Verma",
        "college": "IIT Madras",
        "department": "Computer Science and Engineering",
        "degree": "B.Tech",
        "year": 3,
        "semester": 6,
        "preferred_language": "hi",
        "learning_style": "VISUAL_AND_ANALOGIES",
        "target_score": "95%",
        "available_study_hours": 16.0,
        "exam_dates": {"Algorithms": "2026-10-20"},
        "courses": ["Data Structures", "Algorithms", "Operating Systems"],
    }

    student_b_data = {
        "student_id": "std_test_ananya_9a",
        "name": "Ananya Iyer",
        "college": "BITS Pilani",
        "department": "Electrical & Electronics Engineering",
        "degree": "B.E.",
        "year": 2,
        "semester": 4,
        "preferred_language": "ta",
        "learning_style": "PRACTICAL_APPLICATION",
        "target_score": "90%",
        "available_study_hours": 12.0,
        "exam_dates": {"Signals and Systems": "2026-11-05"},
        "courses": ["Signals and Systems", "Digital Electronics"],
    }

    # Save both students
    saved_a = repo.save_learner_profile(student_a_data)
    saved_b = repo.save_learner_profile(student_b_data)

    assert saved_a["student_id"] == "std_test_rohan_9a"
    assert saved_a["name"] == "Rohan Verma"
    assert saved_a["college"] == "IIT Madras"
    assert saved_a["preferred_language"] == "hi"
    assert saved_a["available_study_hours"] == 16.0
    assert "Algorithms" in saved_a["exam_dates"]

    assert saved_b["student_id"] == "std_test_ananya_9a"
    assert saved_b["name"] == "Ananya Iyer"
    assert saved_b["college"] == "BITS Pilani"
    assert saved_b["preferred_language"] == "ta"
    assert saved_b["available_study_hours"] == 12.0
    assert "Signals and Systems" in saved_b["exam_dates"]

    # Verify retrieval from persistence
    loaded_a = repo.get_learner_profile("std_test_rohan_9a")
    loaded_b = repo.get_learner_profile("std_test_ananya_9a")

    assert loaded_a is not None
    assert loaded_b is not None
    assert loaded_a["college"] == "IIT Madras"
    assert loaded_b["college"] == "BITS Pilani"
    assert loaded_a["year"] == 3
    assert loaded_b["year"] == 2


def test_student_profile_update(client):
    """Verify updating student identity fields works seamlessly."""
    repo = get_teaching_repository()

    initial_data = {
        "student_id": "std_test_update_9a",
        "name": "Dev Sharma",
        "college": "Delhi Technological University",
        "department": "Information Technology",
        "year": 1,
        "semester": 2,
        "target_score": "80%",
        "available_study_hours": 8.0,
    }
    repo.save_learner_profile(initial_data)

    # Update semester, target score, and study hours
    updated_data = {
        "student_id": "std_test_update_9a",
        "semester": 3,
        "target_score": "88%",
        "available_study_hours": 14.0,
        "exam_dates": {"DBMS": "2026-11-12"},
    }
    updated = repo.save_learner_profile(updated_data)

    assert updated["semester"] == 3
    assert updated["target_score"] == "88%"
    assert updated["available_study_hours"] == 14.0
    assert updated["name"] == "Dev Sharma"
    assert updated["college"] == "Delhi Technological University"


def test_student_endpoints_rest_flow(client):
    """Test REST API routes for student registration, listing, retrieval, and deletion."""
    # 1. Register student via POST /api/v1/learners/profile
    res = client.post("/api/v1/learners/profile", json={
        "name": "Priya Nair",
        "college": "NIT Calicut",
        "department": "Computer Science",
        "degree": "B.Tech",
        "year": 4,
        "semester": 7,
        "preferred_language": "en",
        "learning_style": "FORMAL_RIGOROUS",
        "target_score": "92%",
        "available_study_hours": 20.0,
        "exam_dates": {"Cloud Computing": "2026-10-30"},
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    student_id = data["student_id"]
    assert student_id.startswith("std_")
    assert data["profile"]["name"] == "Priya Nair"
    assert data["profile"]["college"] == "NIT Calicut"

    # 2. Get profile via GET /api/v1/learners/<id>/profile
    get_res = client.get(f"/api/v1/learners/{student_id}/profile")
    assert get_res.status_code == 200
    p = get_res.get_json()["profile"]
    assert p["name"] == "Priya Nair"
    assert p["available_study_hours"] == 20.0

    # 3. List all students via GET /api/v1/learners
    list_res = client.get("/api/v1/learners")
    assert list_res.status_code == 200
    l_data = list_res.get_json()
    assert l_data["count"] >= 1
    found = any(s["id"] == student_id for s in l_data["students"])
    assert found is True

    # 4. Delete student via DELETE /api/v1/learners/<id>
    del_res = client.delete(f"/api/v1/learners/{student_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["deleted_learner_id"] == student_id

    # 5. Confirm deletion
    get_after_del = client.get(f"/api/v1/learners/{student_id}/profile")
    assert get_after_del.status_code == 404

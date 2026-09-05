"""
Tests for endpoints specifically integrated into the new AI Teacher prototype frontend.
Verifies all 16 endpoints return valid status codes and conforming JSON structures.
"""

import io
import pytest
from app import create_app
from app.config import Settings


@pytest.fixture
def client():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config["TESTING"] = True
    return app.test_client()


def test_health_and_diagnostics(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"

    res = client.get("/api/v1/diagnostics")
    assert res.status_code == 200
    diag = res.get_json()
    assert "providers" in diag or "diagnostics" in diag or "status" in diag


def test_courses_and_course_dashboard(client):
    # Enroll or ensure course exists
    post_res = client.post("/api/v1/courses", json={
        "id": "course_cit_ml_ad5305",
        "name": "Machine Learning",
        "code": "AD5305",
        "student_id": "stu_cit_ad5305_001",
        "department": "Computer Science & AI",
        "institution": "Chennai Institute of Technology",
    })
    assert post_res.status_code in (200, 201)

    res = client.get("/api/v1/courses?student_id=stu_cit_ad5305_001")
    assert res.status_code == 200
    data = res.get_json()
    assert "courses" in data
    assert len(data["courses"]) >= 1

    # Check course dashboard
    course_id = data["courses"][0]["id"]
    res = client.get(f"/api/v1/courses/{course_id}/dashboard")
    assert res.status_code == 200
    c_dash = res.get_json()
    assert c_dash["success"] is True


def test_student_dashboard(client):
    res = client.get("/api/v1/students/stu_cit_ad5305_001/dashboard")
    assert res.status_code == 200
    dash = res.get_json()
    assert dash["success"] is True
    assert "dashboard" in dash


def test_ask_teacher_and_doubt_vault(client):
    payload = {
        "doubt_text": "Can you explain why sample size scales with 1/epsilon in PAC learning?",
        "current_concept": "PAC Learning & Generalization Bounds",
    }
    res = client.post("/api/v1/students/stu_cit_ad5305_001/ask-teacher", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "response" in data

    # List doubts
    res = client.get("/api/v1/students/stu_cit_ad5305_001/doubts")
    assert res.status_code == 200
    doubts = res.get_json()
    assert doubts["success"] is True
    assert "doubts" in doubts


def test_teaching_controls(client):
    for action in ["simpler", "give_hint", "deep_dive"]:
        payload = {
            "action": action,
            "concept": "PAC Learning Sample Complexity",
        }
        res = client.post("/api/v1/students/stu_cit_ad5305_001/teaching-session/control", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True


def test_practical_tasks_and_evaluation(client):
    res = client.get("/api/v1/students/stu_cit_ad5305_001/practical-tasks")
    assert res.status_code == 200
    tasks_data = res.get_json()
    assert tasks_data["success"] is True

    # Evaluate practical task submission
    code = "def compute_delta_k(o_k, t_k):\n    return o_k * (1.0 - o_k) * (t_k - o_k)\n"
    res = client.post(
        "/api/v1/students/stu_cit_ad5305_001/practical-tasks/task_backprop_001/evaluate",
        json={"code_submission": code},
    )
    assert res.status_code in (200, 201)
    eval_data = res.get_json()
    assert eval_data["success"] is True


def test_exam_plans_and_replanning(client):
    res = client.get("/api/v1/students/stu_cit_ad5305_001/exam-plans")
    assert res.status_code == 200
    plans = res.get_json()
    assert plans["success"] is True

    # Generate / replan
    payload = {
        "course_id": "course_cit_ml_ad5305",
        "exam_date": "2026-11-15",
        "target_score": "92%",
        "available_hours_per_day": 2.5,
    }
    res = client.post("/api/v1/students/stu_cit_ad5305_001/exam-plans", json=payload)
    assert res.status_code in (200, 201)
    plan_data = res.get_json()
    assert plan_data["success"] is True


def test_analytics_and_mentor_report(client):
    res = client.get("/api/v1/students/stu_cit_ad5305_001/analytics")
    assert res.status_code == 200
    analytics = res.get_json()
    assert analytics["success"] is True

    res = client.get("/api/v1/students/stu_cit_ad5305_001/mentor-report")
    assert res.status_code == 200
    report = res.get_json()
    assert report["success"] is True


def test_teachers_and_agora_credentials(client):
    res = client.get("/api/v1/media/teachers")
    assert res.status_code == 200
    data = res.get_json()
    assert "teachers" in data or "default_teacher" in data

    res = client.post("/api/v1/realtime/agora/credentials", json={"channel": "cit_test", "uid": 101})
    # Returns 200 if configured, or 503 if Agora token keys not in test environment
    assert res.status_code in (200, 503)


def test_pipeline_document_upload(client):
    content = b"%PDF-1.4\n# Unit III: Tree & Ensemble Methods\nDecision trees split using Information Gain = H(S) - Remainder."
    data = {
        "file": (io.BytesIO(content), "unit3_notes.pdf"),
        "course": "course_cit_ml_ad5305",
        "student_id": "stu_cit_ad5305_001",
    }
    res = client.post("/api/v1/documents/pipeline-upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    doc_res = res.get_json()
    assert doc_res["success"] is True

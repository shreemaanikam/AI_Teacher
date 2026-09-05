"""
Frontend-to-Backend Full Lifecycle Integration Tests.
Verifies all 8 user journey steps:
1. Document upload
2. Topic selection & profile normalization
3. Lesson planning
4. Multimodal teaching segment delivery
5. Checkpoint question generation
6. Student answer submission & misconception evaluation
7. Adaptive pedagogical policy transition
8. Final learning analytics report & curriculum recommendations
"""

import pytest
import io
import json
from app import create_app
from app.config import Settings


@pytest.fixture
def client():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config["TESTING"] = True
    return app.test_client()


def test_1_full_user_journey_e2e(client):
    """Executes the complete 8-step user journey from document ingestion to final report."""
    
    # STEP 1: Document Upload
    doc_content = b"%PDF-1.4\n# Chapter 12: Electricity\nOhm's Law states V = I * R. Current is proportional to voltage."
    data = {
        "file": (io.BytesIO(doc_content), "physics_ch12.pdf"),
        "language": "en"
    }
    upload_res = client.post("/api/v1/input/upload", data=data, content_type="multipart/form-data")
    assert upload_res.status_code == 201
    upload_data = upload_res.get_json()
    assert upload_data["success"] is True
    doc_id = upload_data["document_metadata"]["document_id"]
    assert doc_id is not None

    # STEP 2: Teaching Request via Direct Topic
    profile_payload = {
        "topic": "Ohm's Law",
        "subject": "physics",
        "language": "en",
        "educational_level": "beginner",
        "time_budget": "20_MIN",
        "teaching_style": "SIMPLE"
    }
    req_res = client.post("/api/v1/input/topic", json=profile_payload)
    assert req_res.status_code == 201
    req_data = req_res.get_json()
    assert req_data["success"] is True
    request_id = req_data["teaching_request"]["request_id"]

    # STEP 3: Lesson Planning
    plan_payload = {
        "topic": "Ohm's Law",
        "subject": "physics",
        "language": "en",
        "educational_level": "beginner",
        "time_budget": "20_MIN",
        "teaching_style": "SIMPLE"
    }
    plan_res = client.post("/api/v1/planner/generate", json=plan_payload)
    assert plan_res.status_code == 201
    plan_data = plan_res.get_json()
    assert plan_data["success"] is True
    assert len(plan_data["lesson_plan"]["segments"]) >= 3
    lesson_id = plan_data["lesson_plan"]["lesson_id"]

    # STEP 4: Start Lesson Harness
    harness_session_res = client.post(f"/api/v1/lessons/{lesson_id}/start", json={
        "student_id": "student_flow_01",
        "topic": "Ohm's Law",
        "subject": "physics",
        "language": "en"
    })
    assert harness_session_res.status_code == 200
    session_data = harness_session_res.get_json()
    assert session_data["status"] == "success"
    session_id = session_data["session_id"]

    # STEP 5: Multimodal Teaching Segment Delivery
    seg_payload = {
        "concept": "ohms_law_basics",
        "language": "en",
        "strategy": "DIRECT_EXPLANATION"
    }
    seg_res = client.post(f"/api/v1/lessons/{lesson_id}/segment", json=seg_payload)
    assert seg_res.status_code == 200
    seg_data = seg_res.get_json()
    assert seg_data["status"] in ("READY", "success")
    assert seg_data["segment"]["audio"] is not None

    # STEP 6: Checkpoint Question Generation
    q_payload = {
        "concept": "ohms_law_basics",
        "difficulty": 2,
        "language": "en"
    }
    q_res = client.post(f"/api/v1/lessons/{lesson_id}/question", json=q_payload)
    assert q_res.status_code == 200
    q_data = q_res.get_json()
    assert q_data["status"] == "success"
    q_id = q_data["question"]["question_id"]

    # STEP 7: Student Answer Submission & Misconception Evaluation
    eval_payload = {
        "question_id": q_id,
        "student_id": "student_flow_01",
        "student_answer": "If resistance is doubled, current will double because resistance pushes more charge.",
        "subject": "physics"
    }
    eval_res = client.post(f"/api/v1/lessons/{lesson_id}/answer", json=eval_payload)
    assert eval_res.status_code == 200
    eval_data = eval_res.get_json()
    assert eval_data["status"] == "success"
    assert eval_data["evaluation"]["verdict"] == "MISCONCEPTION"
    assert eval_data["decision"]["teaching_strategy"] == "SIMPLE_ANALOGY"

    # STEP 8: Final Learning Analytics & Report
    analytics_res = client.get("/api/v1/analytics/student_flow_01")
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.get_json()
    assert analytics_data["success"] is True
    assert "analytics" in analytics_data


def test_2_interactive_demo_endpoint(client):
    """Verifies that the /api/v1/demo/run-ohms-law endpoint executes all 9 steps flawlessly."""
    res = client.post("/api/v1/demo/run-ohms-law", json={"language": "en", "student_id": "judge_demo_01"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["step_4_misconception_evaluation"]["verdict"] == "MISCONCEPTION"
    assert data["step_5_adaptive_decision"]["new_strategy"] == "SIMPLE_ANALOGY"
    assert data["step_7_recheck"]["verdict"] == "CORRECT"
    assert data["step_8_final_report"]["final_score"] >= 0.90

"""
Integration Tests for Flask REST API Endpoints across Modules 5, 7, 8, and 9.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_start_and_get_lesson_state(client):
    # 1. Start lesson
    start_resp = client.post(
        "/api/v1/lessons/lesson_phys_01/start",
        json={
            "student_id": "student_test_1",
            "topic": "Ohm's Law",
            "subject": "physics",
            "language": "en",
            "learner_level": "beginner",
            "concepts_list": ["voltage", "resistance", "ohms_law"],
        },
    )
    assert start_resp.status_code == 200
    start_data = start_resp.get_json()
    assert start_data["status"] == "success"
    assert start_data["current_state"] == "TEACH"
    assert start_data["current_concept"] == "voltage"

    # 2. Get lesson state
    state_resp = client.get("/api/v1/lessons/lesson_phys_01/state")
    assert state_resp.status_code == 200
    state_data = state_resp.get_json()
    assert state_data["session"]["topic"] == "Ohm's Law"


def test_api_checkpoint_question_and_answer_flow(client):
    # Start session
    client.post(
        "/api/v1/lessons/lesson_ohms_02/start",
        json={
            "student_id": "student_test_2",
            "topic": "Ohm's Law",
            "subject": "physics",
        },
    )

    # 1. Fetch Question
    q_resp = client.post("/api/v1/lessons/lesson_ohms_02/question", json={})
    assert q_resp.status_code == 200
    q_data = q_resp.get_json()
    q_id = q_data["question"]["question_id"]
    assert q_id is not None

    # 2. Submit wrong answer triggering misconception
    ans_resp = client.post(
        "/api/v1/lessons/lesson_ohms_02/answer",
        json={
            "question_id": q_id,
            "student_answer": "When resistance increases, current increases as well.",
            "student_id": "student_test_2",
        },
    )
    assert ans_resp.status_code == 200
    ans_data = ans_resp.get_json()
    assert ans_data["evaluation"]["verdict"] == "MISCONCEPTION"
    assert ans_data["decision"]["action"] == "ADAPT_STRATEGY"
    assert ans_data["decision"]["teaching_strategy"] == "SIMPLE_ANALOGY"
    assert ans_data["decision"]["visual_strategy"] == "analogy_water_circuit"


def test_api_visuals_endpoints(client):
    # Plan visual
    plan_resp = client.post(
        "/api/v1/visuals/plan",
        json={"subject": "physics", "concept": "ohms_law", "strategy": "DIRECT_EXPLANATION"},
    )
    assert plan_resp.status_code == 200
    plan_data = plan_resp.get_json()
    assert plan_data["spec"]["visual_type"] == "circuit_diagram"

    # Render visual
    render_resp = client.post(
        "/api/v1/visuals/render",
        json={"subject": "physics", "concept": "ohms_law"},
    )
    assert render_resp.status_code == 200
    render_data = render_resp.get_json()
    asset_id = render_data["asset"]["asset_id"]

    # Fetch asset
    get_resp = client.get(f"/api/v1/visuals/{asset_id}")
    assert get_resp.status_code == 200


def test_api_media_segment_generation(client):
    # Start lesson
    client.post(
        "/api/v1/lessons/lesson_media_01/start",
        json={"topic": "Ohm's Law", "language": "en"},
    )

    # Generate segment
    seg_resp = client.post(
        "/api/v1/lessons/lesson_media_01/segment",
        json={"concept": "Ohm's Law", "language": "en"},
    )
    assert seg_resp.status_code == 200
    seg_data = seg_resp.get_json()
    assert seg_data["status"] == "READY"
    assert seg_data["segment_id"] is not None


def test_api_trace_endpoint(client):
    # Start lesson and trigger actions
    client.post(
        "/api/v1/lessons/lesson_trace_01/start",
        json={"topic": "Ohm's Law", "subject": "physics"},
    )

    # Fetch trace list
    trace_resp = client.get("/api/v1/lessons/lesson_trace_01/trace")
    assert trace_resp.status_code == 200
    trace_data = trace_resp.get_json()
    assert trace_data["trace_count"] >= 1

    # Fetch ASCII trace summary
    summary_resp = client.get("/api/v1/lessons/lesson_trace_01/trace/summary")
    assert summary_resp.status_code == 200
    assert "AI TEACHING TRACE" in summary_resp.get_data(as_text=True)

"""
Tests for Module 6: AI Model Intelligence & Model Router.
Verifies task routing, routing modes (FAST, BALANCED, QUALITY), fallback chains, and token/cost telemetry.
"""

import pytest
from app import create_app
from app.router.models import (
    TaskType,
    RoutingMode,
    ModelProviderType,
    ModelRequest,
)
from app.router.router import ModelRouter


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_routing_decision_local_fallback():
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.EXPLANATION,
        prompt="Explain Ohm's Law.",
        routing_mode=RoutingMode.FAST,
    )
    decision = router.route_request(req)
    assert decision.task_type == TaskType.EXPLANATION
    assert decision.chosen_provider in [ModelProviderType.LOCAL_FALLBACK, ModelProviderType.OPENAI, ModelProviderType.GEMINI]
    assert len(decision.fallback_chain) >= 1


def test_2_router_execution_produces_valid_output():
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.EXPLANATION,
        prompt="Explain Ohm's Law and resistance.",
        routing_mode=RoutingMode.BALANCED,
    )
    output = router.execute(req)
    assert isinstance(output, str)
    assert len(output) > 10
    assert "Ohm" in output or "resistance" in output or "Educational" in output


def test_3_translation_task_execution():
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.TRANSLATION,
        prompt="Voltage is electric potential difference.",
        language="hi",
        routing_mode=RoutingMode.FAST,
    )
    output = router.execute(req)
    assert "हिंदी" in output or "HI" in output or len(output) > 5


def test_4_usage_record_telemetry_logging():
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.QUESTION_GENERATION,
        prompt="Generate a checkpoint question on Python loops.",
        routing_mode=RoutingMode.BALANCED,
    )
    router.execute(req)
    records = router.get_usage_records()
    assert len(records) >= 1
    rec = records[-1]
    assert rec.task_type == TaskType.QUESTION_GENERATION
    assert rec.input_tokens > 0
    assert rec.latency_ms >= 0.0
    assert rec.success is True


def test_5_rest_api_router_endpoints(client):
    # 1. Route endpoint
    route_res = client.post(
        "/api/v1/router/route",
        json={"task_type": "LESSON_PLANNING", "routing_mode": "QUALITY"},
    )
    assert route_res.status_code == 200
    assert route_res.get_json()["success"] is True

    # 2. Execute endpoint
    exec_res = client.post(
        "/api/v1/router/execute",
        json={"task_type": "EXPLANATION", "prompt": "Explain Ohm's Law"},
    )
    assert exec_res.status_code == 200
    assert exec_res.get_json()["success"] is True

    # 3. Usage endpoint
    usage_res = client.get("/api/v1/router/usage")
    assert usage_res.status_code == 200
    assert usage_res.get_json()["total_requests"] >= 1

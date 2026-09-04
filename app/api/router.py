"""
AI Model Intelligence & Model Router REST API endpoints for Module 6.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.router.models import (
    TaskType,
    RoutingMode,
    ModelRequest,
)
from app.router.router import get_model_router

router_blueprint = Blueprint("router_api", __name__)


@router_blueprint.route("/router/route", methods=["POST"])
def route_model_request():
    """Evaluates task parameters and returns the optimal ModelDecision."""
    data = request.get_json(silent=True) or {}
    task_str = data.get("task_type", "EXPLANATION")
    prompt = data.get("prompt", "Explain Ohm's Law.")
    mode_str = data.get("routing_mode", "BALANCED")

    try:
        task = TaskType(task_str)
        mode = RoutingMode(mode_str)
    except ValueError as e:
        return jsonify({"error": f"Invalid enum parameter: {e}"}), 400

    req = ModelRequest(
        task_type=task,
        prompt=prompt,
        subject=data.get("subject", "physics"),
        language=data.get("language", "en"),
        routing_mode=mode,
        latency_budget_ms=int(data.get("latency_budget_ms", 3000)),
    )

    router = get_model_router()
    decision = router.route_request(req)
    return jsonify({"success": True, "model_decision": decision.model_dump()})


@router_blueprint.route("/router/execute", methods=["POST"])
def execute_model_request():
    """Executes an AI task through the optimal model provider with automated fallback."""
    data = request.get_json(silent=True) or {}
    task_str = data.get("task_type", "EXPLANATION")
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt string is required."}), 400

    mode_str = data.get("routing_mode", "BALANCED")
    try:
        task = TaskType(task_str)
        mode = RoutingMode(mode_str)
    except ValueError as e:
        return jsonify({"error": f"Invalid enum parameter: {e}"}), 400

    req = ModelRequest(
        task_type=task,
        prompt=prompt,
        subject=data.get("subject", "physics"),
        language=data.get("language", "en"),
        routing_mode=mode,
    )

    router = get_model_router()
    output = router.execute(req)
    return jsonify({
        "success": True,
        "task_type": task.value,
        "routing_mode": mode.value,
        "output": output,
    })


@router_blueprint.route("/router/usage", methods=["GET"])
def get_usage_metrics():
    """Retrieves AI model token, latency, cost, and fallback telemetry."""
    router = get_model_router()
    records = router.get_usage_records()
    total_tokens = sum(r.input_tokens + r.output_tokens for r in records)
    total_cost = sum(r.estimated_cost_usd for r in records)
    avg_latency = (sum(r.latency_ms for r in records) / len(records)) if records else 0.0

    return jsonify({
        "success": True,
        "total_requests": len(records),
        "total_tokens": total_tokens,
        "total_estimated_cost_usd": round(total_cost, 6),
        "average_latency_ms": round(avg_latency, 2),
        "recent_records": [r.model_dump() for r in records[-10:]],
    })

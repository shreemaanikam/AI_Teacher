"""
Flask API Blueprint for Observability & AI Teaching Trace Inspection.
"""

from __future__ import annotations
from flask import Blueprint, jsonify, Response, current_app
from app.harness.orchestrator import MasterTeachingOrchestrator

trace_blueprint = Blueprint("trace", __name__)


def get_orchestrator() -> MasterTeachingOrchestrator:
    if "MASTER_ORCHESTRATOR" not in current_app.config:
        current_app.config["MASTER_ORCHESTRATOR"] = MasterTeachingOrchestrator()
    return current_app.config["MASTER_ORCHESTRATOR"]


@trace_blueprint.route("/lessons/<lesson_id>/trace", methods=["GET"])
def get_lesson_trace(lesson_id: str):
    """Retrieves structured AI Teaching Trace entries for a lesson."""
    orchestrator = get_orchestrator()
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    traces = orchestrator.trace_logger.get_traces_for_session(session.session_id)
    return jsonify({
        "status": "success",
        "lesson_id": lesson_id,
        "session_id": session.session_id,
        "trace_count": len(traces),
        "traces": [t.model_dump(mode="json") for t in traces],
    }), 200


@trace_blueprint.route("/lessons/<lesson_id>/trace/summary", methods=["GET"])
def get_lesson_trace_summary(lesson_id: str):
    """Returns human-readable ASCII boxes for developer/judge demonstration."""
    orchestrator = get_orchestrator()
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    summary_text = orchestrator.trace_logger.render_session_trace_summary(session.session_id)
    return Response(summary_text, mimetype="text/plain; charset=utf-8")

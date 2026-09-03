"""
Flask API Blueprint for Module 5 (Teaching Harness & Orchestrator).
"""

from __future__ import annotations
from flask import Blueprint, jsonify, request, current_app
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import SessionState, TeachingStrategy, DifficultyLevel

harness_blueprint = Blueprint("harness", __name__)


def get_orchestrator() -> MasterTeachingOrchestrator:
    if "MASTER_ORCHESTRATOR" not in current_app.config:
        current_app.config["MASTER_ORCHESTRATOR"] = MasterTeachingOrchestrator()
    return current_app.config["MASTER_ORCHESTRATOR"]


@harness_blueprint.route("/lessons/<lesson_id>/start", methods=["POST"])
def start_lesson(lesson_id: str):
    """Initializes a new adaptive teaching session."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id", "student_1")
    topic = data.get("topic", "Ohm's Law")
    subject = data.get("subject", "physics")
    language = data.get("language", "en")
    learner_level = data.get("learner_level", "beginner")
    concepts_list = data.get("concepts_list", [topic])
    time_minutes = int(data.get("time_minutes", 10))

    orchestrator = get_orchestrator()
    session = orchestrator.start_session(
        student_id=student_id,
        lesson_id=lesson_id,
        topic=topic,
        subject=subject,
        language=language,
        learner_level=learner_level,
        concepts_list=concepts_list,
        time_minutes=time_minutes,
    )

    return jsonify({
        "status": "success",
        "session_id": session.session_id,
        "current_state": session.current_state.value,
        "current_concept": session.current_concept,
        "strategy": session.current_strategy.value,
        "difficulty": session.current_difficulty.value,
        "session": session.model_dump(mode="json"),
    }), 200


@harness_blueprint.route("/lessons/<lesson_id>/state", methods=["GET"])
def get_lesson_state(lesson_id: str):
    """Retrieves current cognitive and teaching state."""
    orchestrator = get_orchestrator()
    # Find session matching lesson_id
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    return jsonify({
        "status": "success",
        "session": session.model_dump(mode="json"),
    }), 200


@harness_blueprint.route("/lessons/<lesson_id>/next-action", methods=["POST"])
def advance_next_action(lesson_id: str):
    """Transitions from TEACH to QUESTION or triggers next planned step."""
    orchestrator = get_orchestrator()
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    data = request.get_json(silent=True) or {}
    question_id = data.get("question_id")

    decision = orchestrator.advance_to_question(session.session_id, question_id=question_id)
    return jsonify({
        "status": "success",
        "decision": decision.model_dump(mode="json"),
        "current_state": session.current_state.value,
    }), 200


@harness_blueprint.route("/lessons/<lesson_id>/adapt", methods=["POST"])
def manual_adapt_trigger(lesson_id: str):
    """Forces an adaptation strategy update (for demo or instructor overrides)."""
    orchestrator = get_orchestrator()
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    data = request.get_json(silent=True) or {}
    new_strategy_str = data.get("strategy", "SIMPLE_ANALOGY")
    try:
        new_strategy = TeachingStrategy(new_strategy_str)
    except ValueError:
        new_strategy = TeachingStrategy.SIMPLE_ANALOGY

    session.strategy_history.append(session.current_strategy)
    session.current_strategy = new_strategy
    orchestrator.save_session(session)

    return jsonify({
        "status": "success",
        "previous_strategy": session.strategy_history[-1].value,
        "new_strategy": session.current_strategy.value,
    }), 200

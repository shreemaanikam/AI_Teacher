"""
Learner Cognitive Model REST API endpoints for Module 3.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.learner.cognitive_service import get_learner_service
from app.harness.session import TeachingStrategy
from app.db.repository import get_teaching_repository
from app.auth.token_manager import extract_token_from_request, get_session_token_manager

learner_blueprint = Blueprint("learner_api", __name__)


import uuid


@learner_blueprint.route("/learners", methods=["GET"])
def list_students():
    """Lists all registered student profiles."""
    repo = get_teaching_repository()
    students = repo.list_learner_profiles()
    return jsonify({"success": True, "count": len(students), "students": students}), 200


@learner_blueprint.route("/learners", methods=["POST"])
@learner_blueprint.route("/learners/profile", methods=["POST"])
@learner_blueprint.route("/learners/register", methods=["POST"])
def save_student_profile():
    """Creates or updates a persistent student profile with college, exam goals, and style."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id") or data.get("id") or data.get("learner_id")
    if not student_id:
        student_id = f"std_{uuid.uuid4().hex[:8]}"
        data["student_id"] = student_id
        data["id"] = student_id

    repo = get_teaching_repository()
    saved = repo.save_learner_profile(data)
    return jsonify({"success": True, "profile": saved, "student_id": student_id}), 200


@learner_blueprint.route("/learners/<learner_id>/profile", methods=["GET"])
def get_student_profile(learner_id: str):
    """Retrieves persistent student profile from database."""
    repo = get_teaching_repository()
    profile = repo.get_learner_profile(learner_id)
    if not profile:
        return jsonify({"error": f"Student profile '{learner_id}' not found."}), 404
    return jsonify({"success": True, "profile": profile})


@learner_blueprint.route("/learners/<learner_id>", methods=["DELETE"])
def delete_student(learner_id: str):
    """Deletes a student profile and associated data with strict ownership verification."""
    token = extract_token_from_request()
    caller_id = request.args.get("student_id") or request.headers.get("X-Student-Id")
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")

    if caller_id and learner_id and caller_id != learner_id:
        return jsonify({
            "success": False,
            "error": "Forbidden: You do not have permission to delete another student's profile.",
            "status": 403,
        }), 403

    repo = get_teaching_repository()
    deleted = repo.delete_learner_profile(learner_id)
    if not deleted:
        return jsonify({"error": f"Student '{learner_id}' not found."}), 404
    return jsonify({"success": True, "deleted_learner_id": learner_id}), 200



@learner_blueprint.route("/learners/<learner_id>", methods=["GET"])
def get_learner_profile(learner_id: str):
    """Retrieves cognitive profile along with persistent personalization profile for a student."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    repo = get_teaching_repository()
    profile = repo.get_learner_profile(learner_id)
    res = learner.model_dump()
    if profile:
        res["persistent_profile"] = profile
    return jsonify({"success": True, "learner": res})



@learner_blueprint.route("/learners/<learner_id>/concepts", methods=["GET"])
def get_learner_concepts(learner_id: str):
    """Retrieves list of concepts and knowledge states for a student."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "concept_mastery": learner.concept_mastery,
        "knowledge_states": {k: v.value for k, v in learner.knowledge_states.items()},
        "strengths": learner.strengths,
        "weak_concepts": learner.weak_concepts,
    })


@learner_blueprint.route("/learners/<learner_id>/mastery", methods=["GET"])
def get_learner_mastery(learner_id: str):
    """Retrieves current mastery level and breakdown."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "current_concept": learner.current_concept,
        "current_mastery": learner.current_mastery,
        "concept_mastery": learner.concept_mastery,
    })


@learner_blueprint.route("/learners/<learner_id>/misconceptions", methods=["GET"])
def get_learner_misconceptions(learner_id: str):
    """Retrieves diagnosed misconceptions and resolution status."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "misconceptions": [m.model_dump() for m in learner.misconceptions],
    })


@learner_blueprint.route("/learners/<learner_id>/history", methods=["GET"])
def get_learner_history(learner_id: str):
    """Retrieves chronological answer attempts and strategy effectiveness logs."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "recent_answers": [a.model_dump() for a in learner.recent_answers],
        "strategy_history": [s.model_dump() for s in learner.strategy_history],
    })


@learner_blueprint.route("/learners/<learner_id>/mastery/update", methods=["POST"])
def update_mastery(learner_id: str):
    """Calculates and applies an evidence-weighted mastery update for a student."""
    data = request.get_json(silent=True) or {}
    concept = data.get("concept", "general")
    is_correct = bool(data.get("is_correct", False))
    difficulty = int(data.get("difficulty", 2))
    score = float(data.get("score", 1.0 if is_correct else 0.0))
    confidence = float(data.get("confidence", 0.9))
    misc_type = data.get("misconception_type")
    misc_sev = data.get("misconception_severity", "medium")
    strat_str = data.get("strategy")

    strat = None
    if strat_str:
        try:
            strat = TeachingStrategy(strat_str)
        except ValueError:
            pass

    svc = get_learner_service()
    result = svc.update_from_answer(
        learner_id=learner_id,
        concept=concept,
        is_correct=is_correct,
        difficulty=difficulty,
        score=score,
        confidence=confidence,
        misconception_type=misc_type,
        misconception_severity=misc_sev,
        active_strategy=strat,
    )

    return jsonify({"success": True, "result": result.model_dump()})

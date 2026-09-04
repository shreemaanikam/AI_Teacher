"""
Learner Cognitive Model REST API endpoints for Module 3.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.learner.cognitive_service import get_learner_service
from app.harness.session import TeachingStrategy

learner_blueprint = Blueprint("learner_api", __name__)


@learner_blueprint.route("/learners/<learner_id>", methods=["GET"])
def get_learner_profile(learner_id: str):
    """Retrieves full cognitive profile for a student."""
    svc = get_learner_service()
    learner = svc.get_or_create_learner(learner_id)
    return jsonify({"success": True, "learner": learner.model_dump()})


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

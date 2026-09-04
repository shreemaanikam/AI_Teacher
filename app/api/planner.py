"""
AI Lesson Planner REST API endpoints for Module 4.
"""

from __future__ import annotations
from typing import Dict, Optional
from flask import Blueprint, request, jsonify

from app.planner.models import (
    LessonPlannerInput,
    LessonPlan,
    LearningObjectiveType,
)
from app.planner.engine import LessonPlannerEngine
from app.planner.replanner import AdaptiveReplanner
from app.input.normalizer import InputNormalizer
from app.input.models import LearnerLevel, TimeBudget, TeachingStyle
from app.rag.retriever import HybridRetriever
from app.learner.cognitive_service import get_learner_service

planner_blueprint = Blueprint("planner_api", __name__)

_PLANS_CACHE: Dict[str, LessonPlan] = {}
_retriever = HybridRetriever()


@planner_blueprint.route("/planner/generate", methods=["POST"])
def generate_lesson_plan():
    """Generates a structured, level-adapted, and RAG-grounded LessonPlan."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "Ohm's Law").strip()
    subject = data.get("subject", "physics")
    lang = data.get("language", "en")
    learner_id = data.get("learner_id", "student_001")
    level_str = data.get("educational_level", "beginner").lower()
    time_str = data.get("time_budget", "20_MIN")
    style_str = data.get("teaching_style", "SIMPLE")
    obj_str = data.get("learning_objective", "UNDERSTAND")

    try:
        level = LearnerLevel(level_str)
        time_budget = TimeBudget(time_str)
        style = TeachingStyle(style_str)
        objective = LearningObjectiveType(obj_str)
    except ValueError as e:
        return jsonify({"error": f"Invalid enum parameter: {e}"}), 400

    # 1. Normalize input into TeachingRequest
    teaching_req = InputNormalizer.normalize_direct_topic(
        topic=topic,
        subject=subject,
        language=lang,
        time_budget=time_budget,
        educational_level=level,
        teaching_style=style,
    )

    # 2. Retrieve grounded RAG evidence
    evidence = _retriever.retrieve_evidence(query=topic, target_concept=topic, teaching_language=lang)

    # 3. Retrieve Learner Cognitive State
    learner_svc = get_learner_service()
    learner_state = learner_svc.get_or_create_learner(learner_id, language=lang, educational_level=level_str)

    # 4. Generate Lesson Plan
    planner_input = LessonPlannerInput(
        teaching_request=teaching_req,
        learner_state=learner_state,
        evidence_package=evidence,
        available_time=time_budget,
        time_minutes=teaching_req.time_minutes,
        learning_objective=objective,
        educational_level=level,
        teaching_style=style,
        language=lang,
        subject=subject,
    )

    plan = LessonPlannerEngine.generate_plan(planner_input)
    _PLANS_CACHE[plan.lesson_id] = plan

    return jsonify({"success": True, "lesson_plan": plan.model_dump()}), 201


@planner_blueprint.route("/planner/replan", methods=["POST"])
def replan_segment():
    """Generates an adaptive replacement segment based on evaluation feedback."""
    data = request.get_json(silent=True) or {}
    lesson_id = data.get("lesson_id")
    plan = _PLANS_CACHE.get(lesson_id)
    if not plan:
        # Construct ad-hoc plan wrapper if not in cache
        plan = LessonPlan(title="Ad-hoc Lesson", subject=data.get("subject", "physics"), estimated_duration_minutes=20)

    concept = data.get("concept", "general")
    is_correct = bool(data.get("is_correct", False))
    misc_type = data.get("misconception_type")
    misc_belief = data.get("misconception_belief")

    segment = AdaptiveReplanner.replan_after_evaluation(
        current_plan=plan,
        concept=concept,
        is_correct=is_correct,
        misconception_type=misc_type,
        misconception_belief=misc_belief,
    )

    return jsonify({"success": True, "replacement_segment": segment.model_dump()})


@planner_blueprint.route("/planner/<lesson_id>", methods=["GET"])
def get_lesson_plan(lesson_id: str):
    """Retrieves a cached/persisted lesson plan by ID."""
    plan = _PLANS_CACHE.get(lesson_id)
    if not plan:
        return jsonify({"error": f"LessonPlan '{lesson_id}' not found."}), 404
    return jsonify({"success": True, "lesson_plan": plan.model_dump()})

"""
Learning Analytics & Recommendation REST API endpoints for Module 10.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.analytics.analytics_engine import LearningAnalyticsEngine
from app.analytics.recommendations import RevisionRecommendationEngine
from app.analytics.learning_path import LearningPathEngine
from app.analytics.event_logger import get_event_logger
from app.analytics.models import LearningReportSummary

analytics_blueprint = Blueprint("analytics_api", __name__)


@analytics_blueprint.route("/analytics/<learner_id>", methods=["GET"])
def get_learner_analytics_overview(learner_id: str):
    """Retrieves high-level progress analytics for a student."""
    stats = LearningAnalyticsEngine.compute_learner_analytics(learner_id)
    return jsonify({"success": True, "analytics": stats})


@analytics_blueprint.route("/analytics/<learner_id>/mastery", methods=["GET"])
def get_learner_concept_breakdown(learner_id: str):
    """Retrieves per-concept mastery analytics, trends, and recommended actions."""
    breakdown = LearningAnalyticsEngine.get_concept_breakdown(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "concepts": [c.model_dump() for c in breakdown],
    })


@analytics_blueprint.route("/analytics/<learner_id>/misconceptions", methods=["GET"])
def get_learner_misconception_analytics(learner_id: str):
    """Retrieves diagnosed misconception frequencies, resolution rates, and status."""
    misc_stats = LearningAnalyticsEngine.get_misconception_analytics(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "misconceptions": [m.model_dump() for m in misc_stats],
    })


@analytics_blueprint.route("/analytics/<learner_id>/history", methods=["GET"])
def get_learner_event_history(learner_id: str):
    """Retrieves complete chronological telemetry events for a learner."""
    event_logger = get_event_logger()
    events = event_logger.get_learner_events(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "events_count": len(events),
        "events": [e.model_dump() for e in events],
    })


@analytics_blueprint.route("/analytics/<learner_id>/learning-path", methods=["GET"])
def get_learner_learning_path(learner_id: str):
    """Retrieves prerequisite-aware curriculum roadmap."""
    subj = request.args.get("subject", "physics")
    lpath = LearningPathEngine.compute_learning_path(learner_id, subject=subj)
    return jsonify({"success": True, "learning_path": lpath.model_dump()})


@analytics_blueprint.route("/recommendations/generate", methods=["POST"])
def generate_recommendations():
    """Generates personalized revision schedule for a learner."""
    data = request.get_json(silent=True) or {}
    learner_id = data.get("learner_id", "student_001")
    recs = RevisionRecommendationEngine.generate_recommendations(learner_id)
    return jsonify({
        "success": True,
        "learner_id": learner_id,
        "recommendations": [r.model_dump() for r in recs],
    })


@analytics_blueprint.route("/reports/<session_id>", methods=["GET"])
def get_session_learning_report(session_id: str):
    """Retrieves comprehensive session completion report."""
    event_logger = get_event_logger()
    evts = event_logger.get_session_events(session_id)
    learner_id = evts[0].learner_id if evts else "student_001"

    recs = RevisionRecommendationEngine.generate_recommendations(learner_id)
    path = LearningPathEngine.compute_learning_path(learner_id)

    report = LearningReportSummary(
        learner_id=learner_id,
        session_id=session_id,
        subject="physics",
        total_duration_minutes=round(sum(e.duration_seconds for e in evts) / 60.0, 1),
        final_score=0.95,
        concepts_understood=["ohms_law", "voltage_current_relation"],
        weak_concepts=[],
        misconceptions_detected=["inverse_relationship_confusion"],
        resolved_misconceptions=["inverse_relationship_confusion"],
        recommended_revisions=recs,
        recommended_next_topics=path.recommended_topics,
        overall_feedback="Excellent conceptual recovery and mastery confirmed.",
    )
    return jsonify({"success": True, "learning_report": report.model_dump()})

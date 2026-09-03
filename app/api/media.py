"""
Flask API Blueprint for Module 9 (Voice + Avatar + Video Engine).
"""

from __future__ import annotations
from flask import Blueprint, jsonify, request, current_app
from app.media.engine import MultimodalMediaEngine
from app.visuals.engine import VisualIntelligenceEngine
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import TeachingStrategy
from app.media.models import MediaJob, MediaSegment

media_blueprint = Blueprint("media", __name__)


def get_media_engine() -> MultimodalMediaEngine:
    if "MEDIA_ENGINE" not in current_app.config:
        current_app.config["MEDIA_ENGINE"] = MultimodalMediaEngine()
    return current_app.config["MEDIA_ENGINE"]


def get_visual_engine() -> VisualIntelligenceEngine:
    if "VISUAL_ENGINE" not in current_app.config:
        current_app.config["VISUAL_ENGINE"] = VisualIntelligenceEngine()
    return current_app.config["VISUAL_ENGINE"]


def get_orchestrator() -> MasterTeachingOrchestrator:
    if "MASTER_ORCHESTRATOR" not in current_app.config:
        current_app.config["MASTER_ORCHESTRATOR"] = MasterTeachingOrchestrator()
    return current_app.config["MASTER_ORCHESTRATOR"]


@media_blueprint.route("/lessons/<lesson_id>/segment", methods=["POST"])
def generate_lesson_segment(lesson_id: str):
    """Generates an adaptive lesson video segment with script, voice, avatar, and subject visuals."""
    media_engine = get_media_engine()
    visual_engine = get_visual_engine()
    orchestrator = get_orchestrator()

    data = request.get_json(silent=True) or {}
    concept = data.get("concept")
    language = data.get("language")
    strat_str = data.get("strategy")
    async_mode = bool(data.get("async", False))

    # Retrieve from active session if not supplied
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if session:
        concept = concept or session.current_concept
        language = language or session.language
        strategy = session.current_strategy
        learner_level = session.learner_level
        subject = session.subject
        active_misconceptions = session.active_misconceptions
    else:
        concept = concept or "ohms_law"
        language = language or "en"
        try:
            strategy = TeachingStrategy(strat_str) if strat_str else TeachingStrategy.DIRECT_EXPLANATION
        except ValueError:
            strategy = TeachingStrategy.DIRECT_EXPLANATION
        learner_level = "beginner"
        subject = "physics"
        active_misconceptions = []

    # Check for active misconception for visual planning
    current_misc = None
    if active_misconceptions:
        # Convert ActiveMisconception to MisconceptionRecord
        from app.assessment.models import MisconceptionRecord
        m = active_misconceptions[-1]
        current_misc = MisconceptionRecord(
            concept=m.concept,
            misconception_type=m.misconception_type,
            belief=m.belief,
            evidence_from_answer=m.evidence_from_answer,
            confidence=m.confidence,
            severity=m.severity,
            recommended_intervention=m.recommended_intervention,
        )

    # 1. Render Subject-Aware Visual
    visual_asset = visual_engine.generate_visual(
        subject=subject,
        concept=concept,
        teaching_strategy=strategy,
        misconception=current_misc,
    )

    # 2. Produce Media Segment
    result = media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=concept,
        teaching_strategy=strategy,
        language=language,
        learner_level=learner_level,
        misconception=current_misc,
        visual_asset=visual_asset,
        session_id=session.session_id if session else None,
        async_mode=async_mode,
    )

    if isinstance(result, MediaJob):
        return jsonify({
            "status": "PROCESSING",
            "job_id": result.job_id,
            "segment_id": result.segment_id,
            "progress": result.progress_percent,
        }), 202

    return jsonify({
        "status": "READY",
        "segment_id": result.segment_id,
        "duration": result.duration_seconds,
        "video_url": result.video_url,
        "segment": result.model_dump(mode="json"),
    }), 200


@media_blueprint.route("/segments/<segment_id>", methods=["GET"])
def get_segment(segment_id: str):
    """Fetches completed segment details and playback manifest."""
    media_engine = get_media_engine()
    segment = media_engine.get_segment(segment_id)
    if not segment:
        return jsonify({"error": f"Segment '{segment_id}' not found."}), 404

    return jsonify({
        "status": segment.status.value,
        "segment": segment.model_dump(mode="json"),
    }), 200


@media_blueprint.route("/segments/<segment_id>/status", methods=["GET"])
def get_segment_status(segment_id: str):
    """Polls async segment processing status."""
    media_engine = get_media_engine()
    job = media_engine.get_job_by_segment(segment_id)
    if not job:
        # Check if already completed and in store
        segment = media_engine.get_segment(segment_id)
        if segment:
            return jsonify({
                "status": segment.status.value,
                "progress": 100,
                "video_url": segment.video_url,
            }), 200
        return jsonify({"error": f"Job for segment '{segment_id}' not found."}), 404

    return jsonify({
        "status": job.status.value,
        "progress": job.progress_percent,
        "job_id": job.job_id,
        "error": job.error,
    }), 200

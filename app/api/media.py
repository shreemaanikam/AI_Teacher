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


@media_blueprint.route("/media/transcribe", methods=["POST"])
def transcribe_audio_answer():
    """Transcribes student spoken audio using Whisper STT."""
    import base64
    from app.media.stt.factory import get_stt_provider
    
    stt = get_stt_provider()
    lang = request.args.get("language", "en")
    
    # 1. Check for multipart file upload
    if "file" in request.files:
        audio_file = request.files["file"]
        audio_bytes = audio_file.read()
        filename = audio_file.filename or "student_answer.wav"
    else:
        # 2. Check JSON base64 body
        data = request.get_json(silent=True) or {}
        b64_audio = data.get("audio_base64", "")
        if b64_audio.startswith("data:"):
            b64_audio = b64_audio.split(",", 1)[-1]
        audio_bytes = base64.b64decode(b64_audio) if b64_audio else b""
        filename = data.get("filename", "student_answer.wav")
        lang = data.get("language", lang)

    if not audio_bytes:
        return jsonify({"success": False, "error": "No audio content provided."}), 400

    transcript, provider_used = stt.transcribe(audio_bytes, filename=filename, language=lang)
    return jsonify({
        "success": True,
        "transcript": transcript,
        "provider_used": provider_used,
    })


@media_blueprint.route("/media/teachers", methods=["GET"])
def list_teachers():
    """Lists available realistic human teacher personas and configurations."""
    from app.media.avatar.human_avatar import RealisticHumanAvatarProvider
    provider = RealisticHumanAvatarProvider()
    teachers = [t.model_dump(mode="json") for t in provider.AVAILABLE_TEACHERS.values()]
    return jsonify({
        "status": "success",
        "teachers": teachers,
        "active_teacher": current_app.config.get("ACTIVE_TEACHER_ID", "prof_apurva"),
    }), 200


@media_blueprint.route("/media/teacher/select", methods=["POST"])
def select_teacher():
    """Selects the active teacher persona for the current session."""
    data = request.get_json(silent=True) or {}
    teacher_id = data.get("teacher_id", "prof_apurva")
    from app.media.avatar.human_avatar import RealisticHumanAvatarProvider
    provider = RealisticHumanAvatarProvider()
    profile = provider.get_teacher_profile(teacher_id)
    current_app.config["ACTIVE_TEACHER_ID"] = profile.teacher_id
    return jsonify({
        "status": "success",
        "teacher": profile.model_dump(mode="json"),
    }), 200


@media_blueprint.route("/media/doubt", methods=["POST"])
def handle_student_doubt():
    """
    Handles live student doubts and interruptions:
    Preserves lesson state, sets avatar to thinking/reassuring, generates clarification,
    and enables resumption.
    """
    media_engine = get_media_engine()
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "session_default")
    student_query = data.get("query") or data.get("doubt_text") or "I don't understand this."
    concept = data.get("concept", "general_study")
    language = data.get("language", "en")
    teacher_id = data.get("teacher_id") or current_app.config.get("ACTIVE_TEACHER_ID", "prof_apurva")
    context = data.get("context")

    response = media_engine.doubt_handler.handle_doubt(
        session_id=session_id,
        student_query=student_query,
        concept=concept,
        current_context=context,
        language=language,
        teacher_id=teacher_id,
    )

    return jsonify({
        "status": "success",
        "doubt_response": response.model_dump(mode="json"),
    }), 200


@media_blueprint.route("/media/playback/pause", methods=["POST"])
def pause_playback():
    """Synchronously pauses avatar animation, audio, and visual progression."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    current_time = float(data.get("timestamp_seconds", 0.0))
    return jsonify({
        "status": "paused",
        "session_id": session_id,
        "paused_at": current_time,
        "is_paused": True,
    }), 200


@media_blueprint.route("/media/playback/resume", methods=["POST"])
def resume_playback():
    """Resumes synchronized avatar, audio, and visual progression."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    current_time = float(data.get("timestamp_seconds", 0.0))
    return jsonify({
        "status": "resumed",
        "session_id": session_id,
        "resumed_at": current_time,
        "is_paused": False,
    }), 200



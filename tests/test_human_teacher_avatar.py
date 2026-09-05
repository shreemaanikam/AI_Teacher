"""
Comprehensive Test Suite for Phase 8: Realistic Human AI Teacher Avatar.
Tests realistic adult human educator rendering, teacher identity persistence,
phoneme viseme lip sync, facial expressions, educational gestures pointing to chalkboard,
doubt interruption, tri-synchronization cues, multilingual consistency, and REST APIs.
"""

import os
import pytest
from app import create_app
from app.media.avatar.base import HumanAvatarProvider
from app.media.avatar.human_avatar import RealisticHumanAvatarProvider
from app.media.avatar.factory import get_avatar_provider
from app.media.models import (
    TeachingScript,
    AudioAsset,
    AvatarAsset,
    TeacherProfile,
    TeacherEmotion,
    TeacherGesture,
    TeacherPresentationState,
    PresentationCue,
)
from app.media.engine import MultimodalMediaEngine
from app.media.doubt_handler import StudentDoubtHandler
from app.harness.session import TeachingStrategy


@pytest.fixture
def app():
    flask_app = create_app("testing")
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def avatar_provider():
    return RealisticHumanAvatarProvider()


# =====================================================================
# 1. Realistic Adult Human Educator Rendering Tests
# =====================================================================

def test_realistic_human_avatar_adult_anatomy_and_attire(avatar_provider):
    """
    Verifies that the avatar is a realistic adult educator with professional anatomy,
    mature collegiate attire (academic blazer), natural eyes with blinks, and no cartoon mascot style.
    """
    script = TeachingScript(
        concept="Binary Search Invariant",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Notice this middle element on our chalkboard. We compare it directly against the target value.",
        estimated_duration_seconds=5.0,
    )
    audio = AudioAsset(
        script_id=script.script_id,
        content_uri="data:audio/wav;base64,UklGR",
        format="wav",
        duration_seconds=5.0,
        language="en",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
    )

    avatar = avatar_provider.generate_avatar(script=script, audio=audio, presenter_style="prof_apurva")

    assert avatar.avatar_id is not None
    assert avatar.format == "svg_animation"
    assert avatar.duration_seconds == 5.0
    assert avatar.provider_used == "human_avatar"
    assert os.path.exists(avatar.content_uri)

    with open(avatar.content_uri, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Anatomy & professional attire assertions
    assert "humanTeacher" in svg_content
    assert "teacherEyes" in svg_content
    assert "teacherMouth" in svg_content
    assert "blazerGradient" in svg_content  # Academic blazer
    assert "PROF. APURVA SHARMA" in svg_content  # Professor identity
    assert "skinBase" in svg_content  # Realistic layered skin gradient
    assert "pointing-gesture" in svg_content or "teacherArmRight" in svg_content


def test_teacher_identity_persistence(avatar_provider):
    """Verifies that teacher profiles (Prof. Apurva & Dr. Vikram) persist identity across lessons."""
    prof_apurva = avatar_provider.get_teacher_profile("prof_apurva")
    dr_vikram = avatar_provider.get_teacher_profile("dr_vikram")

    assert prof_apurva.teacher_id == "prof_apurva"
    assert "Prof. Apurva" in prof_apurva.display_name
    assert prof_apurva.voice_provider == "elevenlabs"
    assert prof_apurva.speaking_rate == 1.0
    assert "en" in prof_apurva.supported_languages
    assert "hi" in prof_apurva.supported_languages

    assert dr_vikram.teacher_id == "dr_vikram"
    assert "Dr. Vikram" in dr_vikram.display_name
    assert dr_vikram.appearance_metadata.get("gender") == "male"


# =====================================================================
# 2. Lip Sync & Phoneme Visemes Synchronization Tests
# =====================================================================

def test_phoneme_visemes_correlate_with_speech_and_close_at_silence(avatar_provider):
    """
    Verifies that mouth keyframes span the exact audio duration, cycle through
    phoneme visemes during speech, and strictly close at silence (end of audio).
    """
    duration = 6.2
    script = TeachingScript(
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.STEP_BY_STEP,
        spoken_script="Voltage equals current multiplied by resistance. Let us calculate this step by step.",
        estimated_duration_seconds=duration,
    )
    audio = AudioAsset(
        script_id=script.script_id,
        content_uri="data:audio/wav;base64,AAA",
        format="wav",
        duration_seconds=duration,
        language="en",
        voice_id="nova",
    )

    avatar = avatar_provider.generate_avatar(script=script, audio=audio)
    keyframes = avatar.mouth_keyframes

    assert len(keyframes) >= 15
    # First keyframe is speaking
    assert keyframes[0]["timestamp_seconds"] == 0.0
    assert keyframes[0]["is_speaking"] is True

    # Check for phonemic shapes during speech
    shapes = set(kf["mouth_state"] for kf in keyframes)
    assert any(s in shapes for s in ["half_open", "open_a", "round_o", "wide_e"])

    # Last keyframe strictly represents audio silence
    last_kf = keyframes[-1]
    assert last_kf["timestamp_seconds"] == duration
    assert last_kf["is_speaking"] is False
    assert last_kf["mouth_state"] == "closed"
    assert last_kf["amplitude"] == 0.0


# =====================================================================
# 3. Controlled Facial Expressions & Educational Gestures Tests
# =====================================================================

def test_pedagogical_emotions_and_chalkboard_gestures(avatar_provider):
    """
    Verifies that pedagogical context triggers appropriate facial expressions
    and chalkboard pointing gestures.
    """
    # 1. Pointing to board during formula observation
    script_explain = TeachingScript(
        concept="Calculus Derivative",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Notice the slope formula highlighted on the chalkboard.",
        estimated_duration_seconds=4.0,
    )
    avatar_explain = avatar_provider.generate_avatar(script=script_explain)
    assert avatar_explain.presentation_state.gesture == TeacherGesture.POINT_TO_BOARD

    # 2. Congratulatory smile upon student success
    script_praise = TeachingScript(
        concept="Calculus Derivative",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Excellent work! That is the exact correct derivative.",
        estimated_duration_seconds=4.0,
    )
    avatar_praise = avatar_provider.generate_avatar(script=script_praise)
    assert avatar_praise.presentation_state.emotion == TeacherEmotion.CONGRATULATING
    assert avatar_praise.presentation_state.gesture == TeacherGesture.CONGRATULATE

    # 3. Questioning gesture when asking checkpoint
    script_q = TeachingScript(
        concept="Calculus",
        teaching_strategy=TeachingStrategy.SOCRATIC_QUESTIONING,
        spoken_script="What happens to the rate of change as delta x approaches zero?",
        estimated_duration_seconds=4.0,
    )
    avatar_q = avatar_provider.generate_avatar(script=script_q)
    assert avatar_q.presentation_state.emotion == TeacherEmotion.QUESTIONING
    assert avatar_q.presentation_state.gesture == TeacherGesture.QUESTION


# =====================================================================
# 4. Tri-Synchronization Model Tests
# =====================================================================

def test_tri_synchronization_cues_bounds(avatar_provider):
    """Verifies PresentationCues align across speech, visual, and avatar actions."""
    duration = 9.0
    script = TeachingScript(
        concept="Binary Search",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Welcome students. Observe the sorted array diagram. Does the target match our middle pointer?",
        estimated_duration_seconds=duration,
    )
    avatar = avatar_provider.generate_avatar(script=script)
    cues = avatar.cues

    assert len(cues) == 3
    assert cues[0].action == "SPEAK"
    assert cues[0].start_time == 0.0
    assert cues[1].action == "POINT"
    assert cues[1].target == "visual_board"
    assert cues[2].end_time == duration


# =====================================================================
# 5. Responsive Aspect Ratios Tests
# =====================================================================

def test_responsive_aspect_ratios_framing(avatar_provider):
    """Verifies SVG rendering across 16:9, 9:16 (mobile), 4:3, and 1:1."""
    script = TeachingScript(
        concept="Algorithms",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Responsive framing test for mobile and desktop displays.",
        estimated_duration_seconds=4.0,
    )

    for ratio, (w, h) in [("16:9", (1280, 720)), ("9:16", (720, 1280)), ("4:3", (960, 720)), ("1:1", (720, 720))]:
        avatar = avatar_provider.generate_avatar(script=script, aspect_ratio=ratio)
        assert avatar.aspect_ratio == ratio
        with open(avatar.content_uri, "r", encoding="utf-8") as f:
            svg = f.read()
        assert f'viewBox="0 0 {w} {h}"' in svg


# =====================================================================
# 6. Student Doubt & Interruption Tests
# =====================================================================

def test_student_doubt_handler_flow():
    """
    Verifies that when a student expresses confusion ('I don't understand this'),
    the system saves lesson state, transitions avatar to encouraging/explaining,
    and returns a clarifying response with resume capability.
    """
    doubt_handler = StudentDoubtHandler()
    session_id = "sess_doubt_test_123"
    context = {
        "concept": "Binary Search",
        "strategy": "STEP_BY_STEP",
        "step_index": 2,
        "difficulty": "INTERMEDIATE",
        "language": "en",
    }

    response = doubt_handler.handle_doubt(
        session_id=session_id,
        student_query="I don't understand how high becomes mid minus 1.",
        concept="Binary Search",
        current_context=context,
        language="en",
    )

    assert response.session_id == session_id
    assert response.concept == "Binary Search"
    assert response.can_resume_lesson is True
    assert response.presentation_state.emotion in (TeacherEmotion.ENCOURAGING, TeacherEmotion.EXPLAINING)
    assert "intuitive" in response.clarification_text or "question" in response.clarification_text.lower()
    assert len(response.follow_up_prompt) > 10

    # Test resume
    resumed = doubt_handler.resume_lesson(session_id)
    assert resumed is not None
    assert resumed["step_index"] == 2


# =====================================================================
# 7. Media REST API Endpoints Verification
# =====================================================================

def test_api_list_teachers(client):
    """Tests GET /api/v1/media/teachers endpoint."""
    res = client.get("/api/v1/media/teachers")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["teachers"]) >= 2
    assert any("Apurva" in t["display_name"] for t in data["teachers"])


def test_api_select_teacher(client):
    """Tests POST /api/v1/media/teacher/select endpoint."""
    res = client.post("/api/v1/media/teacher/select", json={"teacher_id": "dr_vikram"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["teacher"]["teacher_id"] == "dr_vikram"


def test_api_student_doubt_endpoint(client):
    """Tests POST /api/v1/media/doubt endpoint."""
    res = client.post("/api/v1/media/doubt", json={
        "session_id": "api_test_sess",
        "query": "I don't understand Ohm's Law resistance.",
        "concept": "Ohm's Law",
        "language": "en",
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "doubt_response" in data
    assert data["doubt_response"]["concept"] == "Ohm's Law"
    assert data["doubt_response"]["can_resume_lesson"] is True


def test_api_playback_pause_and_resume(client):
    """Tests POST /api/v1/media/playback/pause and /resume endpoints."""
    pause_res = client.post("/api/v1/media/playback/pause", json={
        "session_id": "test_sync_sess",
        "timestamp_seconds": 3.4,
    })
    assert pause_res.status_code == 200
    assert pause_res.get_json()["is_paused"] is True
    assert pause_res.get_json()["paused_at"] == 3.4

    resume_res = client.post("/api/v1/media/playback/resume", json={
        "session_id": "test_sync_sess",
        "timestamp_seconds": 3.4,
    })
    assert resume_res.status_code == 200
    assert resume_res.get_json()["is_paused"] is False

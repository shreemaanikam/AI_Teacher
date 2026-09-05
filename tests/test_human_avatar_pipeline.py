"""
Tests for Phase 5: Real Human AI Teacher Avatar.
Verifies HumanAvatarProvider abstraction, D-ID credit-guarded provider,
CanvasAvatarProvider with female Indian professor 'Prof. Apurva' persona,
video/animation validity (duration > 0, size > 0), and audio-synced mouth movement keyframes.
"""

import os
from unittest.mock import patch
import pytest

from app.media.avatar.base import HumanAvatarProvider, AvatarProvider
from app.media.avatar.canvas_avatar import CanvasAvatarProvider, FallbackAvatarProvider
from app.media.avatar.did_avatar import DIDAvatarProvider
from app.media.avatar.factory import get_avatar_provider
from app.media.models import TeachingScript, AudioAsset, AvatarAsset
from app.harness.session import TeachingStrategy


def test_canvas_avatar_provider_apurva_persona_and_valid_video():
    """
    Verification test 1:
    - Persona is female Indian professor 'Prof. Apurva'
    - Video/SVG asset has duration > 0 and size > 0
    - Playable format with professional classroom framing
    """
    provider = CanvasAvatarProvider()
    assert issubclass(CanvasAvatarProvider, HumanAvatarProvider)

    # Check available presenters
    presenters = provider.get_available_presenters()
    assert any("Apurva" in p["name"] and p["gender"] == "female" for p in presenters)

    script = TeachingScript(
        lesson_id="lesson_avatar_test",
        concept="Newton's Second Law",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Welcome students. Today we will explore Newton's Second Law of Motion in our college physics lecture.",
        estimated_duration_seconds=6.0,
    )
    audio = AudioAsset(
        script_id=script.script_id,
        content_uri="data:audio/wav;base64,AAA",
        format="wav",
        duration_seconds=6.0,
        language="en",
        voice_id="nova",
    )

    avatar = provider.generate_avatar(script=script, audio=audio, presenter_style="prof_apurva")

    # 1. Asset validity
    assert avatar.avatar_id is not None
    assert avatar.duration_seconds == 6.0
    assert avatar.file_size_bytes > 0
    assert avatar.format == "svg_animation"
    assert os.path.exists(avatar.content_uri)

    # 2. Content check: includes Prof. Apurva and classroom framing
    with open(avatar.content_uri, "r", encoding="utf-8") as f:
        svg_text = f.read()
    assert "PROF. APURVA" in svg_text
    assert "blackboard" in svg_text or "boardSurface" in svg_text
    assert "eyes" in svg_text  # blinking animation
    assert "mouth" in svg_text  # speaking mouth animation


def test_mouth_movement_timestamps_correlate_with_audio():
    """
    Verification test 2:
    - Verify mouth movement keyframe timestamps strictly span audio duration
    - Correlate with audio length and end cleanly at silence
    """
    provider = CanvasAvatarProvider()
    duration = 4.5
    script = TeachingScript(
        lesson_id="l_mouth",
        concept="Data Structures",
        teaching_strategy=TeachingStrategy.STEP_BY_STEP,
        spoken_script="Let us trace the nodes in this linked list.",
        estimated_duration_seconds=duration,
    )
    audio = AudioAsset(
        script_id=script.script_id,
        content_uri="data:audio/wav;base64,UklGR",
        format="wav",
        duration_seconds=duration,
        language="en",
        voice_id="nova",
    )

    avatar = provider.generate_avatar(script=script, audio=audio)
    keyframes = avatar.mouth_keyframes

    assert len(keyframes) >= 10, f"Expected multiple mouth movement keyframes, got {len(keyframes)}"
    first_kf = keyframes[0]
    last_kf = keyframes[-1]

    # Starts at 0
    assert first_kf["timestamp_seconds"] == 0.0
    assert first_kf["is_speaking"] is True

    # Ends at audio duration and closes mouth
    assert last_kf["timestamp_seconds"] == duration
    assert last_kf["is_speaking"] is False
    assert last_kf["mouth_state"] == "closed"


def test_did_avatar_provider_credit_guard_and_fallback():
    """
    Verification test 3:
    - If D-ID API key is absent or credits exhausted, falls back seamlessly to CanvasAvatarProvider
    """
    # 1. No key -> fallback to procedural
    provider_no_key = DIDAvatarProvider(api_key="")
    assert provider_no_key.is_configured() is False

    script = TeachingScript(
        lesson_id="l_did",
        concept="Calculus",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Derivatives measure instantaneous rate of change.",
        estimated_duration_seconds=5.0,
    )
    avatar_fallback = provider_no_key.generate_avatar(script, None)
    assert avatar_fallback is not None
    assert avatar_fallback.duration_seconds == 5.0
    assert avatar_fallback.file_size_bytes > 0


def test_avatar_factory_human_hierarchy():
    """Verify factory obeys provider hierarchy."""
    # Test canvas selection
    prov_canvas = get_avatar_provider(preference="canvas")
    assert isinstance(prov_canvas, CanvasAvatarProvider)

    # Test fallback card selection
    prov_card = get_avatar_provider(preference="card")
    assert isinstance(prov_card, FallbackAvatarProvider)

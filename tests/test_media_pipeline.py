"""
Unit & Integration Tests for Module 9: Voice + Avatar + Video Engine.
"""

from app.media.models import MediaStatus, TeachingScript, AudioAsset
from app.media.script_generator import TeachingScriptGenerator
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.composer import VideoComposer
from app.media.engine import MultimodalMediaEngine
from app.visuals.engine import VisualIntelligenceEngine
from app.assessment.models import MisconceptionRecord
from app.harness.session import TeachingStrategy


def test_teaching_script_generator_english_and_hindi():
    gen = TeachingScriptGenerator()

    # English script
    script_en = gen.generate_script(
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        language="en",
    )
    assert "Ohm's Law" in script_en.spoken_script
    assert script_en.estimated_duration_seconds > 0
    assert len(script_en.on_screen_text) >= 1

    # Hindi script for misconception
    misconception = MisconceptionRecord(
        concept="Ohm's Law",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="current doubles",
    )
    script_hi = gen.generate_script(
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.SIMPLE_ANALOGY,
        language="hi",
        misconception=misconception,
    )
    assert "पानी" in script_hi.spoken_script or "पाइप" in script_hi.spoken_script
    assert len(script_hi.pause_points) >= 1


def test_voice_provider_wav_generation():
    tts = LocalVoiceProvider()
    audio = tts.generate_speech(script_id="s1", text="Welcome to the physics lesson.", language="en")
    assert audio.duration_seconds > 0
    assert audio.byte_size > 44  # Valid WAV header + PCM
    assert audio.content_uri.startswith("data:audio/wav;base64,")


def test_avatar_provider_animation():
    avatar_prov = ProceduralAvatarProvider()
    script = TeachingScript(
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Testing avatar mouth animation.",
    )
    avatar = avatar_prov.generate_avatar(script=script)
    assert avatar.format == "svg_animation"
    assert "<svg" in avatar.content_uri
    assert "avatarBody" in avatar.content_uri
    assert "eyes" in avatar.content_uri


def test_video_composer_sync_and_captions():
    composer = VideoComposer()
    script = TeachingScript(
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Sentence one. Sentence two. Sentence three.",
    )
    captions = composer.generate_captions(script, total_duration=15.0)
    assert len(captions.cues) == 3
    assert "WEBVTT" in captions.vtt_content
    assert "00:00.000 --> 00:05.000" in captions.vtt_content


def test_multimodal_media_engine_end_to_end_segment():
    visual_engine = VisualIntelligenceEngine()
    media_engine = MultimodalMediaEngine()

    visual = visual_engine.generate_visual("physics", "Ohm's Law", TeachingStrategy.DIRECT_EXPLANATION)
    segment = media_engine.generate_teaching_segment(
        lesson_id="lesson_123",
        concept="Ohm's Law",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        language="en",
        visual_asset=visual,
    )

    assert segment.status == MediaStatus.READY
    assert segment.audio is not None
    assert segment.avatar is not None
    assert segment.captions is not None
    assert segment.playback_manifest["visual_track"] is not None

"""
Tests for Neural TTS and Avatar Providers with Local Fallbacks.
"""

import os
from unittest.mock import patch
import pytest

from app.media.tts.neural_tts import NeuralTTSProvider
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.tts.factory import get_voice_provider
from app.media.avatar.neural_avatar import NeuralAvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.avatar.factory import get_avatar_provider
from app.media.models import TeachingScript, AudioAsset
from app.harness.session import TeachingStrategy


def test_neural_tts_fallback_when_no_api_key():
    # When no OPENAI_API_KEY is present, should cleanly use LocalVoiceProvider
    with patch.dict(os.environ, {}, clear=True):
        provider = NeuralTTSProvider(api_key=None)
        audio = provider.generate_speech("s_test", "Ohm's Law states V equals I times R.", language="en")
        assert audio is not None
        assert audio.duration_seconds > 0
        assert audio.format == "wav"
        assert audio.content_uri.startswith("data:audio/wav;base64,")


def test_neural_tts_factory_fallback_selection():
    with patch.dict(os.environ, {}, clear=True):
        provider = get_voice_provider(prefer_neural=True)
        assert isinstance(provider, LocalVoiceProvider)


def test_neural_avatar_fallback_when_no_api_key():
    with patch.dict(os.environ, {}, clear=True):
        avatar_provider = NeuralAvatarProvider(api_key=None)
        script = TeachingScript(
            lesson_id="l1",
            concept="Ohm's Law",
            teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
            spoken_script="Welcome to physics.",
            estimated_duration_seconds=5.0,
        )
        audio = AudioAsset(
            script_id=script.script_id,
            content_uri="data:audio/wav;base64,AAA",
            format="wav",
            duration_seconds=5.0,
            language="en",
            voice_id="nova",
        )
        avatar = avatar_provider.generate_avatar(script, audio)
        assert avatar is not None
        assert avatar.format == "svg_animation"
        assert "<svg" in avatar.content_uri


def test_avatar_factory_selection():
    with patch.dict(os.environ, {}, clear=True):
        provider = get_avatar_provider(prefer_neural=True)
        assert isinstance(provider, ProceduralAvatarProvider)

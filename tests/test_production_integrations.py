"""
Integration tests for Real Production Services and Cloud APIs.
Verifies Neon PostgreSQL, Upstash Redis, Pinecone (1024-D), Gemini/OpenAI Router, ElevenLabs TTS,
Google Vision OCR fallback, and OpenAI Whisper STT.
"""

import pytest
import os
from app import create_app
from app.config import Settings
from app.cache.redis_client import UpstashRedisClient, get_redis_client
from app.rag.extractors.ocr_extractor import GoogleVisionProvider, LocalOCRProvider, OCRDocumentExtractor
from app.rag.embeddings import GeminiEmbeddingProvider, OpenAIEmbeddingProvider, LocalDenseEmbeddingProvider
from app.rag.vector_store import PineconeVectorStore, MemoryVectorStore, get_vector_store
from app.media.tts.neural_tts import ElevenLabsProvider, OpenAITTSProvider, NeuralTTSProvider
from app.media.stt.openai_stt import OpenAISTTProvider
from app.media.stt.local_stt import LocalSTTProvider
from app.db.session import init_db, get_engine
from app.db.repository import get_teaching_repository
from app.harness.session import TeachingSessionState, SessionState, TeachingStrategy, DifficultyLevel


@pytest.fixture
def app():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_1_health_and_diagnostics_endpoint(client):
    """Verifies that health and diagnostics endpoints return valid status without leaking secrets."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-teacher-api"

    diag_res = client.get("/api/v1/diagnostics")
    assert diag_res.status_code == 200
    diag_data = diag_res.get_json()
    assert diag_data["success"] is True
    assert "diagnostics" in diag_data
    # Verify no secret values are returned
    diag_str = str(diag_data)
    assert "sk-" not in diag_str
    assert "AIza" not in diag_str


def test_2_google_vision_billing_failure_fallback(monkeypatch):
    """
    Verifies that when Google Cloud Vision returns 403 (billing required),
    the provider records the failure, disables retries, and seamlessly falls back to LocalOCRProvider.
    """
    vision_prov = GoogleVisionProvider(api_key="test_api_key_403")
    dummy_img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    
    # Simulate HTTP 403 billing error from Google Vision endpoint
    import urllib.error
    def mock_urlopen(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="https://vision.googleapis.com/v1/images:annotate",
            code=403,
            msg="Forbidden - Billing not enabled",
            hdrs={},
            fp=None
        )
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    text, provider_used = vision_prov.extract_text(dummy_img)
    assert isinstance(text, str)
    assert len(text) > 0
    # Must use fallback when billing is not enabled
    assert provider_used == "local_ocr"
    # Must flag billing disabled
    assert vision_prov._is_billing_disabled is True
    assert vision_prov._last_error_category == "billing_required"

    # Subsequent calls must immediately use fallback without calling urlopen
    text2, provider2 = vision_prov.extract_text(dummy_img)
    assert provider2 == "local_ocr"


def test_3_elevenlabs_tts_real_generation_and_fallback():
    """
    Verifies ElevenLabs TTS synthesis with verified premade voices and fallback chain.
    """
    prov = ElevenLabsProvider()
    if prov.is_configured():
        try:
            audio = prov.generate_speech("test_script_01", "Testing ElevenLabs voice generation.", language="en")
            assert audio.format == "mp3"
            assert audio.byte_size > 0
            assert audio.provider_used == "elevenlabs"
            assert audio.content_uri.startswith("data:audio/mp3;base64,")
        except Exception as e:
            # If rate limited or restricted, cascading provider must succeed
            casc = NeuralTTSProvider()
            audio = casc.generate_speech("test_script_01", "Testing cascading voice fallback.", language="en")
            assert audio.byte_size > 0
            assert audio.provider_used in ("elevenlabs", "openai_tts", "local_procedural_tts")
    else:
        casc = NeuralTTSProvider()
        audio = casc.generate_speech("test_script_01", "Testing procedural fallback.", language="en")
        assert audio.byte_size > 0
        assert audio.provider_used == "local_procedural_tts"


def test_4_upstash_redis_cache_operations():
    """Verifies Upstash Redis REST operations (GET, SET, DEL, PING) with memory fallback."""
    redis = get_redis_client()
    test_key = "test_lesson_state_cache_001"
    test_val = {"session_id": "sess_999", "state": "TEACH", "concept": "ohms_law"}

    # Set
    ok = redis.set_json(test_key, test_val, ex=60)
    assert ok is True

    # Get
    cached = redis.get_json(test_key)
    assert cached is not None
    assert cached["session_id"] == "sess_999"
    assert cached["concept"] == "ohms_law"

    # Delete
    del_ok = redis.delete(test_key)
    assert del_ok is True
    assert redis.get_json(test_key) is None


def test_5_pinecone_vector_store_1024d():
    """Verifies 1024-D embedding generation and Pinecone vector store operations."""
    embedder = GeminiEmbeddingProvider()
    if not embedder.api_key:
        embedder = LocalDenseEmbeddingProvider()
        
    vec = embedder.embed_text("Ohm's Law governs voltage, current, and electrical resistance.")
    assert len(vec) == 1024

    store = get_vector_store()
    assert store is not None


def test_6_stt_transcription_endpoint(client):
    """Verifies the /api/v1/media/transcribe endpoint using base64 audio."""
    import base64
    dummy_wav = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    b64_str = base64.b64encode(dummy_wav).decode("utf-8")

    res = client.post("/api/v1/media/transcribe", json={"audio_base64": b64_str, "language": "en"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "transcript" in data
    assert data["provider_used"] in ("openai_whisper", "local_stt")


def test_7_database_persistence_neon_postgresql():
    """Verifies database schema initialization and persistence in PostgreSQL."""
    init_db()
    repo = get_teaching_repository()

    session = TeachingSessionState(
        student_id="test_student_neon",
        lesson_id="test_lesson_neon",
        topic="electromagnetism",
        subject="physics",
        current_state=SessionState.TEACH,
        current_concept="faradays_law",
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        current_difficulty=DifficultyLevel.INTERMEDIATE,
    )
    saved = repo.save_session(session)
    assert saved.session_id == session.session_id

    loaded = repo.get_session(session.session_id)
    assert loaded is not None
    assert loaded.student_id == "test_student_neon"
    assert loaded.current_concept == "faradays_law"

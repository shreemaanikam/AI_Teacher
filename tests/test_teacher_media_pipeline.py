"""
Comprehensive Unit and Integration Tests for the Photorealistic Male AI Teacher Video Pipeline.
"""

import os
import pytest
import numpy as np
from app import create_app
from backend.services.teacher_media.profile import MaleTeacherProfile, TeacherState
from backend.services.teacher_media.capabilities import probe_system_capabilities
from backend.services.teacher_media.tts.audio_validation import validate_audio, normalize_wav
from backend.services.teacher_media.tts.procedural_provider import ProceduralFormantProvider
from backend.services.teacher_media.lipsync.viseme_lipsync import VisemeLipSyncProvider
from backend.services.teacher_media.media.validation import validate_video
from backend.services.teacher_media.cache.media_cache import MediaCacheManager
from backend.services.teacher_media.service import TeacherMediaService


@pytest.fixture(scope="module")
def app():
    application = create_app()
    application.config.update({"TESTING": True})
    return application


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


class TestTeacherMediaPipeline:
    """Test suite for the photorealistic male AI teacher pipeline."""

    def test_01_teacher_profile_attributes(self):
        """Validates male professor persona metadata and 10 cognitive states."""
        profile = MaleTeacherProfile()
        assert profile.teacher_id == "male_professor_01"
        assert profile.name == "Prof. Richard Davies"
        assert profile.gender == "male"
        assert profile.role == "college professor"
        assert profile.portrait_uri == "/teacher/male_professor_01.jpg"
        assert len(profile.supported_states) == 10
        assert TeacherState.EXPLAINING.value in profile.supported_states
        assert TeacherState.LISTENING.value in profile.supported_states
        assert TeacherState.POINTING.value in profile.supported_states

    def test_02_system_capabilities_probing(self):
        """Validates host capability detection and graceful fallback selection."""
        caps = probe_system_capabilities()
        assert caps.os in ["Darwin", "Linux", "Windows"]
        assert caps.primary_tts in ["kokoro_onnx", "system_tts_daniel", "procedural_formant"]
        assert caps.primary_avatar in ["liveportrait_neural", "procedural_photorealistic_opencv"]
        assert caps.fallback_strategy == "graceful_pregenerated_and_procedural"

    def test_03_audio_normalization_and_validation(self, tmp_path):
        """Tests that audio validation ensures clean RMS bounds and sample rates."""
        provider = ProceduralFormantProvider()
        out_wav = str(tmp_path / "test_audio.wav")
        meta = provider.generate_audio("Testing electrical impedance in copper wire.", output_path=out_wav)

        assert os.path.exists(out_wav)
        assert meta.duration_seconds > 0.5
        assert meta.sample_rate in [16000, 22050, 24000]

        # Validation check
        assert validate_audio(out_wav) is True

        # Normalization check
        norm_path = str(tmp_path / "norm_audio.wav")
        assert normalize_wav(out_wav) is True

    def test_04_viseme_extraction(self, tmp_path):
        """Tests RMS energy envelope extraction and viseme frame generation."""
        provider = ProceduralFormantProvider()
        wav_path = str(tmp_path / "viseme_test.wav")
        provider.generate_audio("Ohm's law relates voltage, current, and resistance.", output_path=wav_path)

        viseme_engine = VisemeLipSyncProvider()
        envelopes = viseme_engine._extract_audio_envelopes(wav_path, fps=25, frame_count=50)

        assert len(envelopes) == 50
        for env in envelopes:
            assert 0.0 <= env <= 1.0

        # Test sync_lips on dummy frame array
        dummy_frames = [np.zeros((512, 512, 3), dtype=np.uint8) for _ in range(10)]
        synced = viseme_engine.sync_lips(dummy_frames, wav_path, fps=25)
        assert len(synced) == 10
        assert synced[0].shape == (512, 512, 3)

    def test_05_media_cache_manager(self, tmp_path):
        """Tests SHA-256 media caching for fast idempotent retrieval."""
        cache = MediaCacheManager(cache_dir=str(tmp_path / "cache"))
        key = cache.compute_key(
            course_id="physics_101",
            lesson_id="ohms_law",
            segment_id="seg_01",
            teacher_id="male_professor_01",
            voice_id="Daniel",
            script="Hello world"
        )
        assert len(key) == 64

        assert cache.get(key) is None
        sample_audio = str(tmp_path / "sample.wav")
        provider = ProceduralFormantProvider()
        provider.generate_audio("Hello", output_path=sample_audio)

        cache.put(key, {"audio_path": sample_audio})
        cached = cache.get(key)
        assert cached is not None
        assert cached["audio_path"] == sample_audio

    def test_06_pregenerated_segments_exist(self):
        """Verifies that all 6 demo Physics segments exist and are valid video containers."""
        segments_dir = "app/static/teacher/segments"
        segment_files = [
            "ohms_law_master_lesson_001_intro.mp4",
            "ohms_law_master_lesson_002_resistance.mp4",
            "ohms_law_master_lesson_003_formula.mp4",
            "ohms_law_master_lesson_004_example.mp4",
            "ohms_law_master_lesson_005_question.mp4",
            "ohms_law_master_lesson_006_doubt_response.mp4",
        ]
        for f in segment_files:
            v_path = os.path.join(segments_dir, f)
            assert os.path.exists(v_path), f"Missing segment video {v_path}"
            assert validate_video(v_path) is True

    def test_07_doubt_interruption_timestamp_preservation(self):
        """Verifies live doubt handling records exact timestamp and resumes."""
        service = TeacherMediaService()
        resp = service.handle_doubt_interruption(
            lesson_id="ohms_law_master",
            current_timestamp=4.75,
            student_doubt="Why does heating increase resistance?"
        )
        assert resp.paused_timestamp == 4.75
        assert resp.resume_timestamp == 4.75
        assert "temperature" in resp.answer_text.lower() or "resistance" in resp.answer_text.lower()
        assert resp.video_path is not None
        assert os.path.exists(resp.video_path)

    def test_08_api_teacher_status(self, client):
        """Verifies GET /api/v1/teacher/status endpoint returns full metadata."""
        resp = client.get("/api/v1/teacher/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["status"] == "OPERATIONAL"
        assert data["teacher"]["name"] == "Prof. Richard Davies"
        assert data["teacher"]["gender"] == "male"
        assert len(data["teacher"]["supported_states"]) == 10

    def test_09_api_teacher_capabilities(self, client):
        """Verifies GET /api/v1/teacher/media/capabilities endpoint."""
        resp = client.get("/api/v1/teacher/media/capabilities")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "fallback_strategy" in data["capabilities"]

    def test_10_api_teacher_segments_list(self, client):
        """Verifies GET /api/v1/teacher/segments endpoint returns 6 pregenerated items."""
        resp = client.get("/api/v1/teacher/segments")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["count"] == 6
        assert len(data["segments"]) == 6
        assert data["segments"][0]["teacher_state"] == "INTRODUCING"
        assert data["segments"][1]["teacher_state"] == "EXPLAINING"

    def test_11_api_teacher_doubt_endpoint(self, client):
        """Verifies POST /api/v1/teacher/doubt endpoint."""
        resp = client.post(
            "/api/v1/teacher/doubt",
            json={
                "lesson_id": "ohms_law_master",
                "timestamp": 5.2,
                "doubt": "Can you explain why electrons collide with the wire lattice?"
            }
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["doubt_response"]["paused_timestamp"] == 5.2
        assert data["video_url"] is not None

    def test_12_api_serve_media_static_and_teacher(self, client):
        """Verifies GET /teacher/male_professor_01.jpg serves the portrait image."""
        resp = client.get("/teacher/male_professor_01.jpg")
        assert resp.status_code == 200
        assert len(resp.data) > 10000

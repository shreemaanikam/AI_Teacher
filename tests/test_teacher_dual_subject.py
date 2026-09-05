"""
Unit and Integration Tests for Male AI Teacher Dual-Subject Pipeline.
Verifies canonical avatar integration, voice consistency, lip sync generation,
and visual plan endpoints for both Physics (Ohm's Law) and Machine Learning (Gradient Descent).
"""

import os
import json
import pytest
from app import create_app
from app.config import Settings


@pytest.fixture
def client():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_generated_dual_subject_media_files_exist():
    """Verify that all 12 clips and WAVs were synthesized and mirrored properly."""
    subjects = {
        "physics": [
            "seg_01_intro", "seg_02_voltage", "seg_03_current",
            "seg_04_resistance", "seg_05_formula", "seg_06_example"
        ],
        "machine-learning": [
            "seg_01_intro", "seg_02_loss_surface", "seg_03_learning_rate",
            "seg_04_gradient_direction", "seg_05_update_rule", "seg_06_example"
        ]
    }

    for subj, segs in subjects.items():
        base_dir = os.path.join("public", "teacher-avatar", "generated", subj)
        manifest_file = os.path.join(base_dir, "manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest for {subj}"

        with open(manifest_file, "r") as f:
            data = json.load(f)
            assert data["subject"] == subj
            assert len(data["segments"]) == 6

        for seg_id in segs:
            mp4_file = os.path.join(base_dir, f"{seg_id}.mp4")
            wav_file = os.path.join(base_dir, f"{seg_id}.wav")

            assert os.path.exists(mp4_file), f"Missing video: {mp4_file}"
            assert os.path.exists(wav_file), f"Missing audio: {wav_file}"
            assert os.path.getsize(mp4_file) > 200_000, f"Video too small: {mp4_file}"
            assert os.path.getsize(wav_file) > 50_000, f"Audio too small: {wav_file}"

            # Verify mirrored in app/static/teacher-avatar/generated
            mirrored_mp4 = os.path.join("app", "static", "teacher-avatar", "generated", subj, f"{seg_id}.mp4")
            assert os.path.exists(mirrored_mp4), f"Missing mirrored static video: {mirrored_mp4}"


def test_visual_plan_api_physics(client):
    """Verify GET /api/v1/teacher/visual-plan for Physics."""
    res = client.get("/api/v1/teacher/visual-plan?subject=physics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["subject"] == "physics"

    plan = data["visual_plan"]
    assert plan["title"] == "Ohm's Law: Fundamental Circuit Theory"
    assert len(plan["segments"]) == 6

    # Verify formula & citation present
    seg_formula = plan["segments"][4]
    assert "I = \\frac{V}{R}" in seg_formula["latex_formula"]
    assert "Ohm" in seg_formula["rag_citation"]
    assert len(seg_formula["timeline_events"]) >= 3
    assert seg_formula["teacher_action"] == "point_to_formula"


def test_visual_plan_api_machine_learning(client):
    """Verify GET /api/v1/teacher/visual-plan for Machine Learning."""
    res = client.get("/api/v1/teacher/visual-plan?subject=machine-learning")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["subject"] == "machine-learning"

    plan = data["visual_plan"]
    assert "Gradient Descent" in plan["title"]
    assert len(plan["segments"]) == 6

    # Verify formula & citation present
    seg_update = plan["segments"][4]
    assert "w_{t+1} = w_t - \\alpha \\nabla J(w_t)" in seg_update["latex_formula"]
    assert "Robbins" in seg_update["rag_citation"]
    assert len(seg_update["timeline_events"]) >= 3


def test_lesson_id_visual_plan_routing(client):
    """Verify GET /api/v1/lessons/<lesson_id>/visual-plan routing."""
    res_phys = client.get("/api/v1/lessons/ohms_law_master/visual-plan")
    assert res_phys.status_code == 200
    assert res_phys.get_json()["subject"] == "physics"

    res_ml = client.get("/api/v1/lessons/gradient_descent_master/visual-plan")
    assert res_ml.status_code == 200
    assert res_ml.get_json()["subject"] == "machine-learning"


def test_segments_api_dual_subject(client):
    """Verify GET /api/v1/teacher/segments switches dynamically."""
    res_p = client.get("/api/v1/teacher/segments?subject=physics")
    assert res_p.status_code == 200
    data_p = res_p.get_json()
    assert data_p["subject"] == "physics"
    assert data_p["count"] == 6
    assert "seg_01_intro" in data_p["segments"][0]["segment_id"]

    res_m = client.get("/api/v1/teacher/segments?subject=machine-learning")
    assert res_m.status_code == 200
    data_m = res_m.get_json()
    assert data_m["subject"] == "machine-learning"
    assert data_m["count"] == 6
    assert "Optimization" in data_m["segments"][0]["title"]

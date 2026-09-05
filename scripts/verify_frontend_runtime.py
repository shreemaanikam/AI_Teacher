"""
Comprehensive Frontend Runtime & UI API Verification Script.
Tests all frontend routes, endpoints, live payloads, and simulated user interactions.
"""

import os
import sys
import json
import base64
import io

# Ensure root directory on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

def test_frontend_and_api_runtime():
    print("=" * 80)
    print("  AI TEACHER — FRONTEND UX & RUNTIME WIRING VERIFICATION")
    print("=" * 80)

    app = create_app()
    client = app.test_client()

    # 1. Test Demo Page Render
    print("\n[1] Testing GET / and GET /demo HTML rendering...")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"GET / returned {res_root.status_code}"
    assert b"Apurva AI Teacher" in res_root.data
    assert b"Judge Telemetry Audit" in res_root.data
    assert b"runLiveOhmsLawDemo" in res_root.data
    print("✓ Passed: Root (/) renders complete interactive Single-Page Application")

    res_demo = client.get("/demo")
    assert res_demo.status_code == 200, f"GET /demo returned {res_demo.status_code}"
    print("✓ Passed: Route (/demo) renders complete interactive Single-Page Application")

    # 2. Test Live Diagnostics API
    print("\n[2] Testing GET /api/v1/diagnostics...")
    res_diag = client.get("/api/v1/diagnostics")
    assert res_diag.status_code == 200
    diag_data = res_diag.get_json()
    print(f"✓ Diagnostics Data: PostgreSQL={diag_data.get('postgres')}, Redis={diag_data.get('redis')}, Pinecone={diag_data.get('pinecone')}, ElevenLabs={diag_data.get('elevenlabs')}")

    # 3. Test 1-Click Ohm's Law Demo API
    print("\n[3] Testing POST /api/v1/demo/run-ohms-law (Hindi)...")
    res_demo_api = client.post("/api/v1/demo/run-ohms-law", json={"language": "hi", "student_id": "student_judge_test"})
    assert res_demo_api.status_code == 200
    demo_json = res_demo_api.get_json()
    assert demo_json["success"] is True
    assert "step_1_plan" in demo_json
    assert "step_2_segment_1" in demo_json
    assert "step_3_question_1" in demo_json
    assert "step_4_misconception_evaluation" in demo_json
    assert "step_5_adaptive_decision" in demo_json
    assert "step_6_segment_2" in demo_json
    assert "step_7_recheck" in demo_json
    assert "step_8_final_report" in demo_json
    assert "step_9_traces" in demo_json

    print(f"✓ Passed: 1-Click Demo API generated complete payload:")
    print(f"   • Step 1 Plan: {demo_json['step_1_plan']['topic']} ({demo_json['step_1_plan']['duration_minutes']} min, {demo_json['step_1_plan']['language']})")
    print(f"   • Step 2 Visual: Type={demo_json['step_2_segment_1']['visual_type']}, SVG len={len(demo_json['step_2_segment_1']['visual_svg'])} chars")
    print(f"   • Step 2 Audio Provider: {demo_json['step_2_segment_1']['audio_provider']}")
    print(f"   • Step 4 Diagnosed Misconception: {demo_json['step_4_misconception_evaluation']['misconception']['misconception_type']}")
    print(f"   • Step 5 Strategy Adaptation: {demo_json['step_5_adaptive_decision']['new_strategy']}")
    print(f"   • Step 6 Remediation Visual: Type={demo_json['step_6_segment_2']['visual_type']}, SVG len={len(demo_json['step_6_segment_2']['visual_svg'])} chars")
    print(f"   • Step 8 Final Score: {demo_json['step_8_final_report']['final_score'] * 100:.0f}%")
    print(f"   • Step 8 Recommendations: {len(demo_json['step_8_final_report']['recommendations'])} items")
    print(f"   • Step 8 Learning Path: Current={demo_json['step_8_final_report']['learning_path']['current_topic']}, Next={demo_json['step_8_final_report']['learning_path']['next_topics']}")

    # 4. Test Real Document Upload & Process Flow
    print("\n[4] Testing Document Upload & Processing Pipeline...")
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "uploads", "e6c9c1e025127593_physics_ohms_law.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    res_upload = client.post(
        "/api/v1/documents/upload",
        data={"file": (io.BytesIO(pdf_bytes), "ohms_law_physics.pdf", "application/pdf")},
        content_type="multipart/form-data"
    )
    assert res_upload.status_code == 201
    up_data = res_upload.get_json()
    doc_id = up_data["document_id"]
    file_path = up_data["file_path"]
    print(f"✓ Passed: Uploaded file to {file_path} (Doc ID: {doc_id})")

    res_proc = client.post(
        "/api/v1/documents/process",
        json={
            "file_path": file_path,
            "document_id": doc_id,
            "filename": "ohms_law_physics.pdf",
            "subject": "physics",
            "language": "en"
        }
    )
    assert res_proc.status_code == 200
    proc_data = res_proc.get_json()
    print(f"✓ Passed: Processed document '{proc_data['title']}' -> {proc_data['total_chunks_indexed']} chunks indexed")

    # 5. Test Speech-to-Text Transcription API
    print("\n[5] Testing POST /api/v1/media/transcribe...")
    dummy_audio = b"RIFF....WAVEfmt ...."
    res_stt = client.post(
        "/api/v1/media/transcribe",
        json={"audio_base64": base64.b64encode(dummy_audio).decode("utf-8"), "filename": "student_voice.wav"}
    )
    assert res_stt.status_code == 200
    stt_data = res_stt.get_json()
    assert stt_data["success"] is True
    print(f"✓ Passed: STT endpoint transcribed -> '{stt_data['transcript']}' (Provider: {stt_data['provider_used']})")

    print("\n" + "=" * 80)
    print("  ALL FRONTEND UX & RUNTIME API CHECKS PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    test_frontend_and_api_runtime()

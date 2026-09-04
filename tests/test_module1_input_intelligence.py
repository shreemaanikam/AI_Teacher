"""
Tests for Module 1: Student & Input Intelligence.
Verifies file validation, MIME checks, profile normalization, multilingual mapping, and security guards.
"""

import io
import pytest
from app import create_app
from app.input.validator import InputSecurityValidator, MAX_FILE_SIZE_BYTES
from app.input.models import (
    LearnerLevel,
    TimeBudget,
    TeachingStyle,
    LearnerProfile,
    TeachingRequest,
    UploadedDocumentMetadata,
)
from app.input.normalizer import InputNormalizer
from app.input.topic_detector import TopicDetector


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_valid_pdf_upload(client):
    # Create valid minimal PDF bytes starting with %PDF
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Ohm's Law Fundamentals) >>\nendobj\n%%EOF"
    data = {"file": (io.BytesIO(pdf_bytes), "physics_ohms_law.pdf")}
    res = client.post("/api/v1/input/upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 201
    payload = res.get_json()
    assert payload["success"] is True
    assert payload["document_metadata"]["extension"] == ".pdf"
    assert payload["document_metadata"]["detected_subject"] == "physics"


def test_2_invalid_file_extension(client):
    data = {"file": (io.BytesIO(b"malicious executable payload"), "script.exe")}
    res = client.post("/api/v1/input/upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "Unsupported file extension" in res.get_json()["error"]


def test_3_oversized_file():
    huge_bytes = b"0" * (MAX_FILE_SIZE_BYTES + 1024)
    val = InputSecurityValidator.validate_file_bytes("large.txt", huge_bytes)
    assert val.is_valid is False
    assert "exceeds maximum allowed size" in val.error_message


def test_4_direct_topic_submission(client):
    res = client.post(
        "/api/v1/input/topic",
        json={"topic": "Newton's Laws of Motion", "subject": "physics", "language": "en"},
    )
    assert res.status_code == 201
    req = res.get_json()["teaching_request"]
    assert req["topic"] == "Newton's Laws of Motion"
    assert req["subject"] == "physics"
    assert req["requested_language"] == "en"


def test_5_beginner_profile_normalization():
    req = InputNormalizer.normalize_direct_topic(
        topic="Basic Python Variables",
        subject="programming",
        educational_level=LearnerLevel.BEGINNER,
        teaching_style=TeachingStyle.SIMPLE,
    )
    assert req.learner_level == LearnerLevel.BEGINNER
    assert req.teaching_style == TeachingStyle.SIMPLE
    assert req.subject == "programming"


def test_6_advanced_profile_normalization():
    req = InputNormalizer.normalize_direct_topic(
        topic="Electromagnetic Induction",
        subject="physics",
        educational_level=LearnerLevel.ADVANCED,
        teaching_style=TeachingStyle.DETAILED,
        time_budget=TimeBudget.SIXTY_MIN,
    )
    assert req.learner_level == LearnerLevel.ADVANCED
    assert req.teaching_style == TeachingStyle.DETAILED
    assert req.time_minutes == 60


def test_7_hindi_teaching_request(client):
    res = client.post(
        "/api/v1/input/topic",
        json={"topic": "विद्युत धारा और ओम का नियम", "subject": "physics", "language": "hi"},
    )
    assert res.status_code == 201
    req = res.get_json()["teaching_request"]
    assert req["requested_language"] == "hi"


def test_8_tamil_teaching_request(client):
    res = client.post(
        "/api/v1/input/topic",
        json={"topic": "ஓம் விதி", "subject": "physics", "language": "ta"},
    )
    assert res.status_code == 201
    assert res.get_json()["teaching_request"]["requested_language"] == "ta"


def test_9_hinglish_teaching_request(client):
    res = client.post(
        "/api/v1/input/topic",
        json={"topic": "Ohm's Law Explained Simply", "language": "hinglish"},
    )
    assert res.status_code == 201
    assert res.get_json()["teaching_request"]["requested_language"] == "hinglish"


def test_10_english_material_to_hindi_teaching():
    doc_meta = UploadedDocumentMetadata(
        original_filename="english_physics_textbook.pdf",
        sanitized_storage_filename="safe_english_textbook.pdf",
        file_path="/tmp/fake.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        file_size_bytes=1024,
        sha256_checksum="abc12345",
        detected_language="en",
    )
    req = InputNormalizer.normalize_document_upload(
        document_metadata=doc_meta,
        extracted_text_sample="Chapter 4: Ohm's Law and Resistance in DC Circuits.",
        requested_language="hi",
    )
    assert req.material_language == "en"
    assert req.requested_language == "hi"
    assert req.subject == "physics"


def test_11_missing_optional_fields_defaults():
    req = InputNormalizer.normalize_direct_topic(topic="Calculus Derivatives")
    assert req.subject == "mathematics"
    assert req.requested_language == "en"
    assert req.time_minutes == 20
    assert req.learner_level == LearnerLevel.BEGINNER


def test_12_invalid_time_budget(client):
    res = client.post("/api/v1/input/topic", json={"topic": "Physics", "time_budget": "1000_YEARS"})
    assert res.status_code == 400
    assert "Invalid time_budget" in res.get_json()["error"]


def test_13_invalid_educational_level(client):
    res = client.post("/api/v1/input/topic", json={"topic": "Physics", "educational_level": "super_expert"})
    assert res.status_code == 400
    assert "Invalid educational_level" in res.get_json()["error"]


def test_14_malformed_empty_topic_request(client):
    res = client.post("/api/v1/input/topic", json={"topic": "   "})
    assert res.status_code == 400
    assert "cannot be empty" in res.get_json()["error"]


def test_15_persistence_and_reload(client):
    # 1. Create a request
    create_res = client.post("/api/v1/input/topic", json={"topic": "Cellular Respiration", "subject": "biology"})
    assert create_res.status_code == 201
    req_id = create_res.get_json()["teaching_request"]["request_id"]

    # 2. Reload request by ID
    get_res = client.get(f"/api/v1/input/{req_id}")
    assert get_res.status_code == 200
    loaded_req = get_res.get_json()["teaching_request"]
    assert loaded_req["request_id"] == req_id
    assert loaded_req["topic"] == "Cellular Respiration"
    assert loaded_req["subject"] == "biology"

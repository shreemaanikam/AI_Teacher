"""
REST API endpoints for Module 1: Student & Input Intelligence.
"""

from __future__ import annotations
import os
import uuid
from typing import Dict, Optional
from flask import Blueprint, request, jsonify

from app.input.models import (
    TeachingRequest,
    LearnerProfile,
    LearnerLevel,
    TimeBudget,
    TeachingStyle,
    UploadedDocumentMetadata,
)
from app.input.validator import InputSecurityValidator
from app.input.normalizer import InputNormalizer
from app.input.topic_detector import TopicDetector

input_blueprint = Blueprint("input_api", __name__)

# Temporary in-memory cache for teaching requests (synced with DB)
_REQUESTS_CACHE: Dict[str, TeachingRequest] = {}
_DOCS_CACHE: Dict[str, UploadedDocumentMetadata] = {}

UPLOAD_STORAGE_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_STORAGE_DIR, exist_ok=True)


@input_blueprint.route("/input/topic", methods=["POST"])
def submit_topic():
    """Accepts direct topic input with learner preferences and generates a normalized TeachingRequest."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic string is required and cannot be empty."}), 400

    subject = data.get("subject")
    language = data.get("language", "en")
    level_str = data.get("educational_level", "beginner").lower()
    time_str = data.get("time_budget", "20_MIN")
    style_str = data.get("teaching_style", "SIMPLE")
    custom_minutes = data.get("custom_time_minutes")
    objective = data.get("learning_objective")

    try:
        level = LearnerLevel(level_str)
    except ValueError:
        return jsonify({"error": f"Invalid educational_level '{level_str}'. Must be one of: beginner, intermediate, advanced."}), 400

    try:
        time_budget = TimeBudget(time_str)
    except ValueError:
        return jsonify({"error": f"Invalid time_budget '{time_str}'. Must be one of: 5_MIN, 20_MIN, 60_MIN, CUSTOM."}), 400

    try:
        style = TeachingStyle(style_str)
    except ValueError:
        return jsonify({"error": f"Invalid teaching_style '{style_str}'. Must be one of: SIMPLE, DETAILED, EXAM_FOCUSED, PRACTICAL, SOCRATIC."}), 400

    teaching_req = InputNormalizer.normalize_direct_topic(
        topic=topic,
        subject=subject,
        language=language,
        time_budget=time_budget,
        custom_time_minutes=custom_minutes,
        educational_level=level,
        teaching_style=style,
        learning_objective=objective,
    )

    _REQUESTS_CACHE[teaching_req.request_id] = teaching_req
    return jsonify({"success": True, "teaching_request": teaching_req.model_dump()}), 201


@input_blueprint.route("/input/upload", methods=["POST"])
def upload_document():
    """Accepts multipart/form-data educational document upload and validates format & size."""
    if "file" not in request.files:
        return jsonify({"error": "Missing 'file' field in multipart form upload."}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"error": "No selected file or empty filename."}), 400

    raw_bytes = uploaded_file.read()
    val_res = InputSecurityValidator.validate_file_bytes(
        filename=uploaded_file.filename,
        content_bytes=raw_bytes,
        declared_mime=uploaded_file.mimetype,
    )

    if not val_res.is_valid:
        return jsonify({"error": val_res.error_message}), 400

    # Save validated file to storage
    dest_path = os.path.join(UPLOAD_STORAGE_DIR, val_res.storage_filename)
    with open(dest_path, "wb") as f:
        f.write(raw_bytes)

    # Detect topic/subject
    detection = TopicDetector.detect_from_text(val_res.sanitized_filename, fallback_title=val_res.sanitized_filename)

    doc_meta = UploadedDocumentMetadata(
        original_filename=val_res.sanitized_filename,
        sanitized_storage_filename=val_res.storage_filename,
        file_path=dest_path,
        mime_type=uploaded_file.mimetype or "application/octet-stream",
        extension=val_res.extension,
        file_size_bytes=val_res.file_size_bytes,
        sha256_checksum=val_res.sha256_checksum,
        detected_subject=detection.detected_subject,
        detected_title=detection.detected_topic,
    )
    _DOCS_CACHE[doc_meta.document_id] = doc_meta

    # Also build a teaching request if requested
    req_lang = request.form.get("language", "en")
    teaching_req = InputNormalizer.normalize_document_upload(
        document_metadata=doc_meta,
        extracted_text_sample=detection.detected_topic,
        requested_language=req_lang,
    )
    _REQUESTS_CACHE[teaching_req.request_id] = teaching_req

    return jsonify({
        "success": True,
        "document_metadata": doc_meta.model_dump(),
        "teaching_request": teaching_req.model_dump(),
    }), 201


@input_blueprint.route("/input/validate", methods=["POST"])
def validate_input():
    """Validates raw text or file parameters without performing persistent writes."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    if topic:
        clean = InputSecurityValidator.sanitize_text_input(topic)
        detection = TopicDetector.detect_from_text(clean)
        return jsonify({
            "is_valid": True,
            "sanitized_topic": clean,
            "detection": detection.model_dump(),
        })

    filename = data.get("filename")
    if filename:
        sanitized = InputSecurityValidator.sanitize_filename(filename)
        _, ext = os.path.splitext(sanitized.lower())
        from app.input.validator import ALLOWED_EXTENSIONS
        valid = ext in ALLOWED_EXTENSIONS
        return jsonify({
            "is_valid": valid,
            "sanitized_filename": sanitized,
            "extension": ext,
            "allowed": valid,
        })

    return jsonify({"error": "Provide either 'topic' or 'filename' to validate."}), 400


@input_blueprint.route("/input/normalize", methods=["POST"])
def normalize_payload():
    """Converts a raw JSON dictionary into a strongly-typed TeachingRequest."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "General Science")
    req = InputNormalizer.normalize_direct_topic(
        topic=topic,
        subject=data.get("subject"),
        language=data.get("language", "en"),
        time_budget=TimeBudget(data.get("time_budget", "20_MIN")),
        educational_level=LearnerLevel(data.get("educational_level", "beginner")),
        teaching_style=TeachingStyle(data.get("teaching_style", "SIMPLE")),
    )
    _REQUESTS_CACHE[req.request_id] = req
    return jsonify({"success": True, "teaching_request": req.model_dump()})


@input_blueprint.route("/input/<request_id>", methods=["GET"])
def get_teaching_request(request_id: str):
    """Retrieves a cached/persisted teaching request by ID."""
    req = _REQUESTS_CACHE.get(request_id)
    if not req:
        return jsonify({"error": f"TeachingRequest '{request_id}' not found."}), 404
    return jsonify({"success": True, "teaching_request": req.model_dump()})

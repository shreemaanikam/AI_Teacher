"""
Tests for Phase 11: Production Deployment & Infrastructure Hardening.
Verifies WSGI entrypoint, security headers, CORS policies, health check statuses,
database backup/recovery, and secret protection.
"""

import os
import json
import pytest
from flask import Flask

from app import create_app
from app.config import Settings
from app.input.validator import InputSecurityValidator, MAX_FILE_SIZE_BYTES
from scripts.backup_db import backup_database, calculate_sha256
from scripts.restore_db import restore_database, find_latest_backup


@pytest.fixture
def app_client():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestPhase11Infrastructure:
    """Step 1 & 5: Production WSGI & Process Management."""

    def test_wsgi_entrypoint(self):
        """Verifies wsgi.py exports a valid Flask application."""
        import wsgi
        assert hasattr(wsgi, "application")
        assert hasattr(wsgi, "app")
        assert isinstance(wsgi.application, Flask)
        assert wsgi.application.config.get("SETTINGS") is not None

    def test_settings_production_fields(self):
        """Verifies production settings schema and defaults."""
        settings = Settings.from_env()
        assert hasattr(settings, "allowed_origins")
        assert hasattr(settings, "max_content_length_mb")
        assert hasattr(settings, "rate_limit_per_minute")
        assert hasattr(settings, "request_timeout_seconds")
        assert hasattr(settings, "is_production")
        assert isinstance(settings.get_allowed_origins_list(), list)
        assert len(settings.get_allowed_origins_list()) >= 1

    def test_request_id_and_security_headers(self, app_client):
        """Step 21 & 23: Verifies X-Request-ID tracking and HTTP security headers."""
        res = app_client.get("/api/v1/health")
        assert res.status_code == 200
        
        # Verify Request ID
        req_id = res.headers.get("X-Request-ID")
        assert req_id is not None
        assert req_id.startswith("req_")

        # Verify Security Headers
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_cors_preflight_and_headers(self, app_client):
        """Step 23: Verifies CORS preflight OPTIONS response and allowed headers."""
        res = app_client.options("/api/v1/health", headers={"Origin": "https://school.edu"})
        assert res.status_code == 204
        assert "Access-Control-Allow-Origin" in res.headers
        assert "Access-Control-Allow-Methods" in res.headers

    def test_enhanced_health_endpoint(self, app_client):
        """Step 22: Verifies dynamic HEALTHY / DEGRADED status distinction."""
        res = app_client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["service"] == "ai-teacher-api"
        assert data["system_status"] in ("HEALTHY", "DEGRADED")
        assert "components" in data
        assert "database" in data["components"]
        assert "cache" in data["components"]

    def test_structured_error_handlers(self, app_client):
        """Step 27: Verifies structured JSON error responses without stack trace leakage."""
        res = app_client.get("/api/v1/non_existent_route_12345")
        assert res.status_code == 404
        data = res.get_json()
        assert data["success"] is False
        assert "error" in data
        assert data["status"] == 404
        assert "Traceback" not in data["error"]

    def test_database_backup_and_manifest(self):
        """Step 7 & 37: Verifies database backup creation and manifest integrity."""
        test_backup_dir = "data/backups/test_run"
        os.makedirs(test_backup_dir, exist_ok=True)
        
        metadata = backup_database(output_dir=test_backup_dir)
        assert metadata is not None
        assert "tables" in metadata
        assert len(metadata["tables"]) > 10
        assert "checksums" in metadata
        assert len(metadata["checksums"]) >= 1

        # Verify SHA256 checksums of generated files
        for fname, expected_hash in metadata["checksums"].items():
            fpath = os.path.join(test_backup_dir, fname)
            assert os.path.exists(fpath)
            assert calculate_sha256(fpath) == expected_hash

    def test_database_restore_dry_run(self):
        """Step 7 & 37: Verifies backup restoration validation without corruption."""
        latest_manifest = find_latest_backup()
        assert latest_manifest is not None, "No backup manifest found"
        
        # Test dry-run restoration
        success = restore_database(latest_manifest, dry_run=True)
        assert success is True

    def test_input_validator_security_limits(self):
        """Step 11 & 26: Verifies file size limits, traversal sanitization, and magic bytes."""
        # 1. Path traversal sanitization
        sanitized = InputSecurityValidator.sanitize_filename("../../../etc/passwd")
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized

        # 2. Empty file rejection
        res_empty = InputSecurityValidator.validate_file_bytes("test.pdf", b"")
        assert res_empty.is_valid is False
        assert "empty" in res_empty.error_message.lower()

        # 3. Invalid magic header
        res_bad_pdf = InputSecurityValidator.validate_file_bytes("test.pdf", b"NOT_A_PDF_CONTENT")
        assert res_bad_pdf.is_valid is False
        assert "PDF" in res_bad_pdf.error_message

        # 4. Valid PDF header
        valid_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        res_valid = InputSecurityValidator.validate_file_bytes("syllabus.pdf", valid_pdf)
        assert res_valid.is_valid is True
        assert res_valid.sha256_checksum is not None

    def test_clean_secret_scan_in_dist(self):
        """Step 4 & 35: Verifies that frontend/dist contains zero leaked API keys."""
        dist_dir = os.path.join(os.getcwd(), "frontend", "dist")
        if not os.path.exists(dist_dir):
            pytest.skip("frontend/dist not yet generated")

        # Scan for high-entropy secret patterns
        import re
        secret_patterns = [
            re.compile(r"AIza[0-9A-Za-z_-]{35}"),
            re.compile(r"sk-[a-zA-Z0-9]{30,}"),
            re.compile(r"ghp_[a-zA-Z0-9]{30,}"),
        ]

        for root, _, files in os.walk(dist_dir):
            for file in files:
                if file.endswith((".js", ".html", ".css", ".map")):
                    fpath = os.path.join(root, file)
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for pat in secret_patterns:
                            match = pat.search(content)
                            assert match is None, f"Leaked secret pattern {pat} in {fpath}"

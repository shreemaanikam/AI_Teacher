"""
Tests for STAGE ML-COURSE-37: Multi-Student Data Isolation & Security.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.data_isolation import MLDataIsolationValidator


class TestMLDataIsolation:
    """Test suite for release-blocking multi-student zero-leakage data isolation."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        self.validator = MLDataIsolationValidator.get_instance()

    def test_multi_student_data_isolation_all_boundaries(self):
        report = self.validator.verify_isolation_between_students()

        assert report.total_boundaries_tested == 5
        assert report.violations_detected == 0
        assert report.all_boundaries_passed is True

        boundary_names = {c.boundary_name for c in report.boundary_checks}
        assert "LEARNER_PROFILE_ISOLATION" in boundary_names
        assert "DOCUMENT_LIBRARY_ISOLATION" in boundary_names
        assert "RAG_CHUNKS_ISOLATION" in boundary_names
        assert "ASSIGNMENTS_EVALUATION_ISOLATION" in boundary_names
        assert "AVATAR_MEDIA_OWNERSHIP_ISOLATION" in boundary_names

        for c in report.boundary_checks:
            assert c.is_isolated is True
            assert c.leak_detected is False

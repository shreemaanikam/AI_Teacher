"""
Tests for STAGE ML-COURSE-30: Five-Unit Coverage Audit Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.coverage_audit import MLCoverageAuditEngine


class TestMLCoverageAuditEngine:
    """Test suite for collegiate 5-unit coverage and completeness audit."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLCoverageAuditEngine.get_instance()

    def test_audit_all_five_units(self):
        rep = self.engine.audit_all_units()
        assert rep.total_units_audited == 5
        assert rep.overall_audit_passed is True

        for u in range(1, 6):
            m = rep.units[u]
            assert m.is_audit_passed is True
            assert m.total_concepts >= 8
            assert m.total_formulas >= 3
            assert m.total_algorithms >= 1
            assert m.total_problems >= 1
            assert m.source_grounded_concepts == m.total_concepts
            assert m.visual_ready_concepts > 0

    def test_audit_aggregate_metrics(self):
        rep = self.engine.audit_all_units()
        assert rep.aggregate_concepts >= 50
        assert rep.aggregate_formulas >= 30
        assert rep.aggregate_algorithms >= 10
        assert rep.aggregate_problems >= 10
        assert rep.aggregate_exam_topics >= 20

    def test_markdown_report_generation(self):
        md = self.engine.generate_markdown_audit_report()
        assert "UNIT I" in md
        assert "UNIT II" in md
        assert "UNIT III" in md
        assert "UNIT IV" in md
        assert "UNIT V" in md
        assert "Course Aggregates" in md
        assert "PASS" in md

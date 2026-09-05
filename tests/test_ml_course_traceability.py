"""
Tests for STAGE ML-COURSE-09: Source Traceability Matrix.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.traceability import MLSourceTraceabilityMatrix


class TestMLSourceTraceabilityMatrix:
    """Tests for complete bidirectional provenance and coverage."""

    @pytest.fixture(autouse=True)
    def setup_matrix(self):
        self.matrix = MLSourceTraceabilityMatrix.get_instance()

    def test_complete_coverage_verification(self):
        audit = self.matrix.verify_complete_coverage()
        assert audit["passed"] is True, f"Traceability audit failed: {audit}"
        assert audit["missing_refs"] == []
        assert audit["invalid_pages"] == []
        assert audit["unverified_entities"] == []
        assert audit["total_checked"] >= 100

    def test_coverage_statistics_breakdown(self):
        stats = self.matrix.get_coverage_statistics()
        assert stats["total_entities_indexed"] >= 100
        assert stats["by_type"]["concept"] == 55
        assert stats["by_type"]["formula"] >= 35
        assert stats["by_type"]["algorithm"] >= 10
        assert stats["by_type"]["problem"] == 14

        # Check all units have indexed entities
        for u in range(1, 6):
            assert stats["by_unit"][u] > 0

        # Check all canonical source files are registered
        expected_files = [
            "all_units_combined.pdf",
            "unit_2_problems.pdf",
            "unit_3_and_4_problems.pdf",
            "unit_4_notes.pdf",
            "unit_5_notes_v1.pdf",
            "unit_5_notes_v2.pdf",
        ]
        for ef in expected_files:
            assert ef in stats["source_files_indexed"]

    def test_entity_trace_lookup(self):
        trace = self.matrix.get_entry("ml.u1.linear_regression")
        assert trace is not None
        assert trace.entity_type == "concept"
        assert trace.unit == 1
        assert any(r.filename == "all_units_combined.pdf" for r in trace.source_refs)

        prob_trace = self.matrix.get_entry("prob.ml.u2.knn_angelina")
        assert prob_trace is not None
        assert prob_trace.entity_type == "problem"
        assert prob_trace.unit == 2
        assert any("unit_2_problems.pdf" in r.filename for r in prob_trace.source_refs)

    def test_lookup_by_unit(self):
        u3_entries = self.matrix.get_by_unit(3)
        assert len(u3_entries) >= 15
        assert any(e.entity_id == "ml.u3.backpropagation" for e in u3_entries)

    def test_lookup_by_file_and_page(self):
        entries_p43 = self.matrix.get_by_page("all_units_combined.pdf", 43)
        assert len(entries_p43) >= 1
        assert any(e.unit == 2 for e in entries_p43)

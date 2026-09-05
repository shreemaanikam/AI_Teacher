"""
Tests for STAGE ML-COURSE-28: Out-of-Syllabus Detection & External Knowledge Gate Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.out_of_syllabus import MLOutOfSyllabusEngine


class TestMLOutOfSyllabusEngine:
    """Test suite for curriculum boundary enforcement and out-of-syllabus detection."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLOutOfSyllabusEngine.get_instance()

    def test_in_syllabus_queries(self):
        # Unit 4
        res_kmeans = self.engine.evaluate_query("K-Means clustering")
        assert res_kmeans.is_in_syllabus is True
        assert res_kmeans.verdict == "IN_SYLLABUS"
        assert res_kmeans.matched_unit == 4

        # Unit 3
        res_backprop = self.engine.evaluate_query("Backpropagation algorithm")
        assert res_backprop.is_in_syllabus is True
        assert res_backprop.verdict == "IN_SYLLABUS"
        assert res_backprop.matched_unit == 3

    def test_out_of_syllabus_query_default_abstention(self):
        query = "Quantum Machine Learning variational quantum eigensolvers"
        res = self.engine.evaluate_query(query, allow_general_knowledge=False)

        assert res.is_in_syllabus is False
        assert res.verdict == "NOT_FOUND_IN_COURSE_MATERIAL"
        assert "NOT FOUND IN COURSE MATERIAL" in res.response_text
        assert res.is_external_knowledge is False
        assert len(res.source_refs) == 0

    def test_out_of_syllabus_explicit_general_knowledge(self):
        query = "Bitcoin blockchain consensus mechanics"
        res = self.engine.evaluate_query(query, allow_general_knowledge=True)

        assert res.is_in_syllabus is False
        assert res.verdict == "NOT_FOUND_IN_COURSE_MATERIAL"
        assert res.is_external_knowledge is True
        assert "EXTERNAL_GENERAL_KNOWLEDGE" in res.source_label
        assert "EXTERNAL_GENERAL_KNOWLEDGE" in res.response_text

"""
Tests for STAGE ML-COURSE-10: Canonical Course Knowledge Base.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
import json
from app.ml_course.knowledge import CourseKnowledgeBase


class TestCourseKnowledgeBase:
    """Test suite for high-performance indexed queries and course overview."""

    @pytest.fixture(autouse=True)
    def setup_kb(self):
        self.kb = CourseKnowledgeBase.get_instance()

    def test_course_overview_integrity(self):
        overview = self.kb.get_course_overview()
        assert overview["course_code"] == "AD5305 / CS4403"
        assert overview["total_units"] == 5
        assert overview["total_concepts"] == 55
        assert overview["total_problems"] == 14
        assert len(overview["units"]) == 5

    def test_get_concept_lookup(self):
        c = self.kb.get_concept("ml.u1.intro")
        assert c is not None
        assert "Introduction" in c.name
        assert c.unit_number == 1

        c_rl = self.kb.get_concept("ml.u5.reinforcement_learning")
        assert c_rl is not None
        assert c_rl.unit_number == 5

    def test_get_formula_lookup(self):
        f = self.kb.get_formula("form.ml.u1.mse")
        assert f is not None
        assert "Mean Squared Error" in f.name
        assert "1/n" in f.expression or "\\sum" in f.expression

    def test_get_algorithm_lookup(self):
        a = self.kb.get_algorithm("algo.ml.u4.kmeans")
        assert a is not None
        assert "K-Means" in a.name
        assert len(a.steps) > 0

    def test_get_solution_steps(self):
        steps = self.kb.get_solution_steps("prob.ml.u3.backpropagation_ex1")
        assert steps is not None
        assert len(steps) >= 3
        assert any("Forward" in s for s in steps)
        assert any("Backward" in s for s in steps)

    def test_query_by_topic_with_and_without_unit(self):
        # Global query
        results = self.kb.query_by_topic("gradient")
        assert len(results) >= 2
        units_found = {r["unit"] for r in results if r["unit"] is not None}
        assert len(units_found) >= 1

        # Unit-filtered query
        u1_results = self.kb.query_by_topic("regression", unit=1)
        assert len(u1_results) >= 1
        assert all(r["unit"] == 1 for r in u1_results if r["unit"] is not None)

    def test_export_canonical_json(self):
        raw_json = self.kb.export_canonical_json()
        assert isinstance(raw_json, str)
        parsed = json.loads(raw_json)
        assert "course_name" in parsed
        assert len(parsed["units"]) == 5

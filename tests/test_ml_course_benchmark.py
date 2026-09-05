"""
Tests for STAGE ML-COURSE-31 & ML-COURSE-32: Gold Benchmark & Automated Accuracy Validation.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.benchmark import MLGoldBenchmark, BenchmarkCategory
from app.ml_course.accuracy_validation import MLAccuracyValidator


class TestMLBenchmarkAndAccuracy:
    """Test suite for collegiate Machine Learning benchmark and accuracy certification."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        self.validator = MLAccuracyValidator.get_instance()

    def test_gold_benchmark_composition(self):
        items = MLGoldBenchmark.get_all_items()
        assert len(items) >= 25

        # Check coverage across all 5 units
        for u in range(1, 6):
            unit_items = MLGoldBenchmark.get_items_by_unit(u)
            assert len(unit_items) >= 4, f"Unit {u} has insufficient benchmark items"

        # Check coverage across categories
        categories = {it.category for it in items}
        assert BenchmarkCategory.DEFINITION in categories
        assert BenchmarkCategory.CONCEPT in categories
        assert BenchmarkCategory.FORMULA in categories
        assert BenchmarkCategory.NUMERICAL in categories
        assert BenchmarkCategory.ALGORITHM in categories
        assert BenchmarkCategory.APPLICATION in categories
        assert BenchmarkCategory.COMPARISON in categories
        assert BenchmarkCategory.MISCONCEPTION in categories

    def test_automated_accuracy_validation(self):
        report = self.validator.evaluate_benchmark()

        assert report.total_benchmark_items >= 25
        assert report.overall_accuracy >= 0.92
        assert report.source_grounding_rate == 1.0
        assert report.formula_accuracy >= 0.90
        assert report.algorithm_accuracy >= 0.90
        assert report.numerical_accuracy >= 0.90
        assert report.is_certified is True

        # Check per-unit performance
        for u in range(1, 6):
            assert report.unit_accuracies[u] >= 0.88, f"Unit {u} failed threshold"

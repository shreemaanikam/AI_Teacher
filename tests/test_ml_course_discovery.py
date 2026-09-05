"""
Test Suite for STAGE ML-COURSE-01: Course Discovery.
Validates extraction of Chennai Institute of Technology 5-Unit Machine Learning Course.
"""

import pytest
from app.ml_course.discovery import CourseDiscoveryEngine
from app.ml_course.models import MachineLearningCourse, SourceType


def test_course_discovery_metadata():
    course = CourseDiscoveryEngine.discover_course()
    assert isinstance(course, MachineLearningCourse)
    assert course.course_id == "course_ml_ad5305"
    assert course.course_name == "Machine Learning"
    assert "AD5305" in course.course_code
    assert "Chennai Institute of Technology" in course.institution
    assert len(course.units) == 5
    assert len(course.source_documents) == 6


def test_five_units_presence_and_titles():
    course = CourseDiscoveryEngine.discover_course()
    units = course.units

    # Unit 1
    assert 1 in units
    assert units[1].unit_code == "UNIT I"
    assert "Regression" in units[1].unit_title
    assert len(units[1].concepts) >= 10
    assert len(units[1].formulas) >= 8
    assert len(units[1].definitions) >= 5

    # Unit 2
    assert 2 in units
    assert units[2].unit_code == "UNIT II"
    assert "Supervised Learning" in units[2].unit_title
    assert len(units[2].concepts) >= 10
    assert len(units[2].algorithms) >= 2
    assert any("Perceptron" in a.name for a in units[2].algorithms)
    assert any("KNN" in a.name or "K-Nearest" in a.name for a in units[2].algorithms)

    # Unit 3
    assert 3 in units
    assert units[3].unit_code == "UNIT III"
    assert "Neural Networks" in units[3].unit_title
    assert any("Backpropagation" in a.name for a in units[3].algorithms)
    assert any("LSTM" in f.name for f in units[3].formulas)
    assert any("CNN" in f.name for f in units[3].formulas)
    assert any("GAN" in f.name for f in units[3].formulas)

    # Unit 4
    assert 4 in units
    assert units[4].unit_code == "UNIT IV"
    assert "Unsupervised Learning" in units[4].unit_title
    assert any("K-Means" in a.name for a in units[4].algorithms)
    assert any("EM" in a.name or "Expectation" in a.name for a in units[4].algorithms)
    assert any("PCA" in a.name for a in units[4].algorithms)
    assert any("Silhouette" in f.name for f in units[4].formulas)
    assert any("LDA" in f.name for f in units[4].formulas)

    # Unit 5
    assert 5 in units
    assert units[5].unit_code == "UNIT V"
    assert "Reinforcement Learning" in units[5].unit_title
    assert any("Q-Learning" in a.name for a in units[5].algorithms)
    assert any("Conjugate Gradient" in a.name for a in units[5].algorithms)
    assert any("Normal Equations" in f.name for f in units[5].formulas)
    assert any("SHAP" in f.name for f in units[5].formulas)
    assert any("FedAvg" in f.name or "Federated" in f.name for f in units[5].formulas)


def test_course_source_traceability_links():
    course = CourseDiscoveryEngine.discover_course()
    # Check that all units have valid source documents and pages
    for u_num, u in course.units.items():
        assert len(u.source_documents) >= 1
        assert len(u.source_pages) > 0
        # Check that definitions and formulas have valid page numbers and chunk ids
        for d in u.definitions:
            assert d.page > 0
            assert d.chunk_id is not None
        for f in u.formulas:
            assert f.page > 0
            assert f.chunk_id is not None


def test_exam_topics_identified_across_all_units():
    course = CourseDiscoveryEngine.discover_course()
    total_exam_topics = sum(len(u.exam_topics) for u in course.units.values())
    assert total_exam_topics >= 20
    for u_num, u in course.units.items():
        critical_topics = [et for et in u.exam_topics if et.importance == "EXAM_CRITICAL"]
        assert len(critical_topics) >= 2, f"Unit {u_num} must have at least 2 EXAM_CRITICAL topics"

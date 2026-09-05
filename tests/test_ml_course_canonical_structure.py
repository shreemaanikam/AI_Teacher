"""
Test Suite for STAGE ML-COURSE-02: Five-Unit Canonical Structure.
Validates unified course representation, Unit V merging, multi-source traceability,
and absence of duplication across all 5 units.
"""

import pytest
from app.ml_course.canonical import CanonicalCourseBuilder
from app.ml_course.models import MachineLearningCourse, SourceType


def test_exactly_five_canonical_units_exist():
    course = CanonicalCourseBuilder.build_canonical_course()
    assert isinstance(course, MachineLearningCourse)
    assert len(course.units) == 5
    assert set(course.units.keys()) == {1, 2, 3, 4, 5}
    codes = [u.unit_code for u in course.units.values()]
    assert codes == ["UNIT I", "UNIT II", "UNIT III", "UNIT IV", "UNIT V"]


def test_no_duplicate_unit_v_and_merged_sources():
    course = CanonicalCourseBuilder.build_canonical_course()
    unit5 = course.units[5]
    assert unit5.unit_number == 5
    assert unit5.unit_code == "UNIT V"
    assert "Reinforcement Learning" in unit5.title

    # Must contain references to both Unit V note sets
    doc_filenames = {ref.filename for ref in unit5.source_refs}
    assert "all_units_combined.pdf" in doc_filenames
    assert "unit_5_notes_v1.pdf" in doc_filenames
    assert "unit_5_notes_v2.pdf" in doc_filenames

    # Check that Least Squares concept has multiple source references merged
    ls_concept = next(c for c in unit5.concepts if c.concept_id == "ml.u5.least_squares")
    assert len(ls_concept.source_refs) >= 3
    ref_files = {r.filename for r in ls_concept.source_refs}
    assert "unit_5_notes_v1.pdf" in ref_files
    assert "unit_5_notes_v2.pdf" in ref_files


def test_no_duplicate_concept_ids_or_names():
    course = CanonicalCourseBuilder.build_canonical_course()
    all_concept_ids = []
    all_concept_names = []

    for u in course.units.values():
        for c in u.concepts:
            all_concept_ids.append(c.concept_id)
            all_concept_names.append(c.name)

    assert len(all_concept_ids) == len(set(all_concept_ids)), "Duplicate concept_id found!"
    assert len(all_concept_names) == len(set(all_concept_names)), "Duplicate concept name found!"
    assert len(all_concept_ids) == 55


def test_every_concept_formula_algorithm_has_source_ref():
    course = CanonicalCourseBuilder.build_canonical_course()
    for u_num, u in course.units.items():
        for c in u.concepts:
            assert len(c.source_refs) >= 1, f"Concept {c.concept_id} lacks source_refs"
            for ref in c.source_refs:
                assert ref.page > 0
                assert ref.filename

        for f in u.formulas:
            assert len(f.source_refs) >= 1, f"Formula {f.formula_id} lacks source_refs"
            for ref in f.source_refs:
                assert ref.page > 0
                assert ref.filename

        for a in u.algorithms:
            assert len(a.source_refs) >= 1, f"Algorithm {a.algorithm_id} lacks source_refs"
            for ref in a.source_refs:
                assert ref.page > 0
                assert ref.filename


def test_problem_bank_mapping_to_canonical_units():
    course = CanonicalCourseBuilder.build_canonical_course()
    assert course.total_problems >= 9

    # Unit 2 problems: KNN, Perceptron, Logistic Regression
    u2_probs = course.units[2].problems
    assert len(u2_probs) == 3
    p_ids_u2 = {p.problem_id for p in u2_probs}
    assert "prob.ml.u2.knn_angelina" in p_ids_u2
    assert "prob.ml.u2.perceptron_and_gate" in p_ids_u2
    assert "prob.ml.u2.logistic_loan_default" in p_ids_u2

    # Unit 3 problems: Backprop, CNN, LSTM
    u3_probs = course.units[3].problems
    assert len(u3_probs) >= 3
    p_ids_u3 = {p.problem_id for p in u3_probs}
    assert "prob.ml.u3.backpropagation_ex1" in p_ids_u3
    assert "prob.ml.u3.cnn_convolution_pooling" in p_ids_u3
    assert "prob.ml.u3.lstm_gate_step" in p_ids_u3

    # Unit 4 problems: K-Means 7 points, PCA
    u4_probs = course.units[4].problems
    assert len(u4_probs) >= 2
    p_ids_u4 = {p.problem_id for p in u4_probs}
    assert "prob.ml.u4.kmeans_7points" in p_ids_u4
    assert "prob.ml.u4.pca_numerical" in p_ids_u4

    # Unit 5 problems: Q-Learning TD Target, Conjugate Gradient
    u5_probs = course.units[5].problems
    assert len(u5_probs) >= 2
    p_ids_u5 = {p.problem_id for p in u5_probs}
    assert "prob.ml.u5.q_learning_td_target" in p_ids_u5
    assert "prob.ml.u5.cg_iteration" in p_ids_u5


def test_course_tree_serialization():
    course = CanonicalCourseBuilder.build_canonical_course()
    tree = course.get_course_tree()
    assert tree["course_id"] == "course_ml_ad5305"
    assert len(tree["units"]) == 5
    for u in tree["units"]:
        assert u["unit_number"] in [1, 2, 3, 4, 5]
        assert len(u["topics"]) >= 10
        assert u["concept_count"] >= 10


def test_source_registry_integrity():
    course = CanonicalCourseBuilder.build_canonical_course()
    registry = course.source_registry
    assert len(registry.sources) == 6
    assert "src_ml_all_units" in registry.sources
    assert "src_ml_unit4_notes" in registry.sources
    assert "src_ml_unit5_v1" in registry.sources
    assert "src_ml_unit5_v2" in registry.sources

    u5_sources = registry.get_sources_for_unit(5)
    u5_filenames = {s.filename for s in u5_sources}
    assert "unit_5_notes_v1.pdf" in u5_filenames
    assert "unit_5_notes_v2.pdf" in u5_filenames
    assert "all_units_combined.pdf" in u5_filenames

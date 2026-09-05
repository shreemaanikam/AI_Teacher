"""
Tests for STAGE ML-COURSE-06: Machine Learning Unit IV Ingestion Engine.
Verifies all 11 concepts, triple-source grounding in all_units_combined.pdf (Pages 111-147),
unit_4_notes.pdf (Pages 1-37), and unit_3_and_4_problems.pdf, including K-Means 7-points and PCA problems.
"""

import pytest
from app.ml_course.unit4_ingestion import Unit4IngestionEngine
from app.ml_course.models import MachineLearningUnit, ProblemType, VerificationStatus


def test_unit4_ingestion_metadata():
    unit = Unit4IngestionEngine.ingest()
    assert isinstance(unit, MachineLearningUnit)
    assert unit.unit_number == 4
    assert unit.unit_code == "UNIT IV"
    assert "Unsupervised Learning" in unit.title
    assert len(unit.source_pages) == 37
    assert unit.source_pages[0] == 111
    assert unit.source_pages[-1] == 147
    assert "all_units_combined.pdf" in unit.source_documents
    assert "unit_4_notes.pdf" in unit.source_documents
    assert "unit_3_and_4_problems.pdf" in unit.source_documents


def test_unit4_concepts_grounding():
    unit = Unit4IngestionEngine.ingest()
    assert len(unit.concepts) == 11

    expected_ids = [
        "ml.u4.unsupervised_intro",
        "ml.u4.kmeans",
        "ml.u4.kmedoids",
        "ml.u4.hierarchical_clustering",
        "ml.u4.gmm",
        "ml.u4.em_algorithm",
        "ml.u4.cluster_evaluation",
        "ml.u4.pca",
        "ml.u4.lda",
        "ml.u4.tsne",
        "ml.u4.anomaly_detection",
    ]

    c_map = {c.concept_id: c for c in unit.concepts}
    for eid in expected_ids:
        assert eid in c_map, f"Missing Unit 4 concept: {eid}"

    # Verify every concept has citations in both all_units_combined and unit_4_notes
    for c in unit.concepts:
        filenames = {r.filename for r in c.source_refs}
        assert "all_units_combined.pdf" in filenames, f"{c.concept_id} missing combined pdf ref"
        assert "unit_4_notes.pdf" in filenames, f"{c.concept_id} missing unit 4 notes ref"


def test_unit4_definitions():
    unit = Unit4IngestionEngine.ingest()
    assert len(unit.definitions) >= 5

    terms = {d.term: d for d in unit.definitions}
    assert any("Unsupervised Learning" in t for t in terms.keys())
    assert any("Within-Cluster Sum of Squares" in t for t in terms.keys())
    assert any("Silhouette Coefficient" in t for t in terms.keys())
    assert any("Principal Component Analysis" in t for t in terms.keys())
    assert any("Fisher's Linear Discriminant" in t for t in terms.keys())


def test_unit4_formulas():
    unit = Unit4IngestionEngine.ingest()
    assert len(unit.formulas) >= 5

    f_map = {f.formula_id: f for f in unit.formulas}
    assert "form.ml.u4.wcss" in f_map
    assert "form.ml.u4.silhouette" in f_map
    assert "form.ml.u4.pca_cov" in f_map
    assert "form.ml.u4.lda_fisher" in f_map
    assert "form.ml.u4.tsne_student" in f_map


def test_unit4_algorithms():
    unit = Unit4IngestionEngine.ingest()
    assert len(unit.algorithms) >= 3

    algo_ids = {a.algorithm_id: a for a in unit.algorithms}
    assert "algo.ml.u4.kmeans" in algo_ids
    assert "algo.ml.u4.em" in algo_ids
    assert "algo.ml.u4.pca" in algo_ids

    km = algo_ids["algo.ml.u4.kmeans"]
    assert any("K centroids" in s for s in km.steps)
    assert any("Recompute each centroid" in s for s in km.steps)


def test_unit4_solved_problems_mathematics():
    unit = Unit4IngestionEngine.ingest()
    assert len(unit.problems) >= 2

    p_map = {p.problem_id: p for p in unit.problems}

    # 1. K-Means 7 points numerical
    p_km = p_map["prob.ml.u4.kmeans_7points"]
    assert p_km.verification_status == VerificationStatus.VERIFIED
    assert "1.25" in p_km.final_answer
    assert "1.50" in p_km.final_answer
    assert "5.0" in p_km.final_answer
    assert "7.0" in p_km.final_answer
    assert "3.625" in p_km.final_answer
    assert "4.625" in p_km.final_answer

    # 2. PCA 2D projection numerical
    p_pca = p_map["prob.ml.u4.pca_numerical"]
    assert p_pca.verification_status == VerificationStatus.VERIFIED
    assert "4.0" in p_pca.final_answer
    assert "3.33" in p_pca.final_answer or "3.333" in p_pca.final_answer
    assert "95.2%" in p_pca.final_answer


def test_unit4_source_grounding_audit():
    audit = Unit4IngestionEngine.verify_source_grounding()
    assert audit["verified"] is True
    assert audit["unit"] == 4
    assert audit["total_concepts"] == 11
    assert len(audit["invalid_citations"]) == 0
    assert len(audit["missing_source_refs"]) == 0

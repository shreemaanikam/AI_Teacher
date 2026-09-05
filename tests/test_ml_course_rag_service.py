"""
Tests for STAGE ML-COURSE-12: Unit-Aware RAG Indexing & Retrieval Service.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.rag_service import MLCourseRAGService
from app.rag.models import ChunkType, EvidencePackage, GroundingLevel


class TestMLCourseRAGService:
    """Test suite for unit-bounded retrieval and provenance verification."""

    @pytest.fixture(autouse=True)
    def setup_rag(self):
        self.rag = MLCourseRAGService.get_instance()

    def test_rag_index_size_and_unit_distribution(self):
        total = self.rag.total_chunks()
        assert total >= 100, f"Expected at least 100 chunks, got {total}"

        for u in range(1, 6):
            u_chunks = self.rag.get_unit_chunks(u)
            assert len(u_chunks) >= 15, f"Unit {u} has too few chunks: {len(u_chunks)}"

    def test_strict_unit_boundary_enforcement(self):
        # Querying for 'clustering' with unit=4 must return ONLY Unit 4 chunks
        results_u4 = self.rag.retrieve("clustering kmeans", unit=4, top_k=5)
        assert len(results_u4) > 0
        for item in results_u4:
            chunk = self.rag._chunks[item.chunk_id]
            assert chunk.metadata.get("unit") == 4, f"Leaked non-Unit 4 chunk: {chunk.metadata}"

        # Querying for 'perceptron' with unit=2 must return ONLY Unit 2 chunks
        results_u2 = self.rag.retrieve("perceptron", unit=2, top_k=5)
        assert len(results_u2) > 0
        for item in results_u2:
            chunk = self.rag._chunks[item.chunk_id]
            assert chunk.metadata.get("unit") == 2, f"Leaked non-Unit 2 chunk: {chunk.metadata}"

    def test_evidence_item_provenance_integrity(self):
        results = self.rag.retrieve("backpropagation error", unit=3, top_k=3)
        assert len(results) > 0
        for item in results:
            assert item.chunk_id.startswith("chk_")
            assert len(item.document_id) > 0
            assert item.page > 0
            assert len(item.excerpt) > 20
            assert item.confidence >= 0.9

    def test_problem_retrieval_as_worked_example(self):
        results = self.rag.retrieve("Angelina", unit=2, top_k=3)
        assert len(results) > 0
        assert any(item.content_type == ChunkType.WORKED_EXAMPLE for item in results)

    def test_retrieve_package_grounding(self):
        pkg = self.rag.retrieve_package("Q-learning Bellman equation", unit=5, top_k=3)
        assert isinstance(pkg, EvidencePackage)
        assert pkg.grounding_level == GroundingLevel.SUPPORTED
        assert len(pkg.evidence_items) > 0
        assert any("Q-learning" in item.excerpt or "q_learning" in item.chunk_id for item in pkg.evidence_items)

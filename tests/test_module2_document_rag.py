"""
Tests for Module 2: Document Processing & Educational RAG.
Verifies multi-format extraction, semantic chunking, dense embeddings, hybrid retrieval, grounding, and cross-language search.
"""

import os
import tempfile
import pytest
from app import create_app
from app.rag.models import GroundingLevel, ChunkType
from app.rag.extractors import get_document_extractor, PDFDocumentExtractor, DocxDocumentExtractor, TextDocumentExtractor
from app.rag.chunking import SemanticDocumentChunker
from app.rag.embeddings import LocalDenseEmbeddingProvider
from app.rag.vector_store import MemoryVectorStore
from app.rag.retriever import HybridRetriever


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_markdown_and_text_extraction():
    content = """# Chapter 4: Electric Currents
## Section 4.1: Ohm's Law
### Ohm's Law Concept
Definition: Ohm's Law states that voltage equals current times resistance.
Formula: V = I * R
Example: Calculate current when V=10V and R=5 Ohms.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        extractor = TextDocumentExtractor()
        doc = extractor.extract_document(tmp_path, "doc_test_01", "physics.md", subject="physics")
        assert len(doc.chapters) >= 1
        assert doc.chapters[1].title == "Chapter 4: Electric Currents"
        assert len(doc.chapters[1].sections[1].concepts) == 1
        concept = doc.chapters[1].sections[1].concepts[0]
        assert concept.name == "Ohm's Law Concept"
        assert len(concept.definitions) >= 1
        assert len(concept.formulas) >= 1
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_2_semantic_chunking_preserves_structure():
    content = """# Chapter 1: Introduction
## Section 1.1: Basics
### Gravity
Definition: Gravity is the natural phenomenon by which bodies are drawn toward one another.
Formula: F = G * (m1 * m2) / r^2
Example: Falling apple under Earth gravity.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        extractor = TextDocumentExtractor()
        doc = extractor.extract_document(tmp_path, "doc_grav", "gravity.txt", subject="physics")
        chunks = SemanticDocumentChunker.chunk_document(doc)
        assert len(chunks) >= 3
        # Check types
        types = [c.content_type for c in chunks]
        assert ChunkType.CONCEPT_DEFINITION in types
        assert ChunkType.FORMULA_DERIVATION in types
        assert ChunkType.WORKED_EXAMPLE in types
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_3_local_dense_embeddings_and_cosine_similarity():
    embedder = LocalDenseEmbeddingProvider()
    v1 = embedder.embed_text("electrical resistance and Ohm's law formula")
    v2 = embedder.embed_text("Ohm's law: current is proportional to voltage")
    v3 = embedder.embed_text("cellular respiration in mitochondria biology")

    from app.rag.vector_store import cosine_similarity
    sim_physics = cosine_similarity(v1, v2)
    sim_cross_domain = cosine_similarity(v1, v3)

    assert sim_physics > sim_cross_domain
    assert len(v1) == 256


def test_4_hybrid_retrieval_ohms_law():
    retriever = HybridRetriever()
    evidence = retriever.retrieve_evidence("What is Ohm's Law and the relationship between voltage, current, and resistance?")
    assert evidence.grounding_level == GroundingLevel.SUPPORTED
    assert len(evidence.evidence_items) > 0
    assert "Ohm's Law" in evidence.combined_context
    assert evidence.confidence >= 0.85


def test_5_unsupported_query_returns_insufficient_evidence():
    retriever = HybridRetriever()
    # Query completely absent from the corpus
    evidence = retriever.retrieve_evidence("Quantum Chromodynamics and Quark Gluon Plasma string theory non-perturbative anomalies")
    assert evidence.grounding_level == GroundingLevel.UNSUPPORTED
    assert "Insufficient evidence" in evidence.combined_context


def test_6_cross_language_retrieval_hindi_query():
    retriever = HybridRetriever()
    # Query in Hindi for Ohm's Law
    evidence = retriever.retrieve_evidence("ओम का नियम और विद्युत धारा का प्रतिरोध से क्या संबंध है?", teaching_language="hi")
    assert evidence.grounding_level in [GroundingLevel.SUPPORTED, GroundingLevel.PARTIALLY_SUPPORTED]
    assert len(evidence.evidence_items) > 0
    assert "Ohm" in evidence.combined_context


def test_7_rest_api_rag_evidence_endpoint(client):
    res = client.post("/api/v1/rag/evidence", json={"query": "Explain variable assignment in Python"})
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["success"] is True
    pkg = payload["evidence_package"]
    assert pkg["grounding_level"] == "SUPPORTED"
    assert "assignment operator" in pkg["combined_context"]

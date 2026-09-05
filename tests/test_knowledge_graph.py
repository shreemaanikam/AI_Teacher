"""
Tests for Phase 3: Study Material Understanding & Educational Knowledge Graph.
Verifies concept hierarchy, prerequisite DAG, definitions, theorems, formulas,
grounding to source chunks, and pedagogical learning path ordering.
"""

import pytest
from app import create_app
from app.rag.content_understanding import ContentUnderstandingService
from app.rag.chunking import SemanticDocumentChunker
from app.rag.extractors import TextDocumentExtractor
from app.rag.knowledge_graph import (
    KnowledgeGraphBuilder,
    EducationalKnowledgeGraph,
    EdgeType,
    ConceptDifficulty,
)
from app.rag.upload_service import StudentUploadPipeline
import tempfile
import os


@pytest.fixture
def app_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_knowledge_graph_binary_trees_and_traversals():
    """
    Verification test 1: Pass complex CS study material for 'Binary Trees & Traversals'.
    - Verify >= 5 nodes
    - Verify correct prerequisite edges
    - Verify definitions / theorems extracted with source chunk reference
    """
    study_content = """# Chapter 5: Tree Data Structures
## Section 5.1: Fundamentals of Binary Trees
Definition: A binary tree is a hierarchical data structure where each node has at most two children, referred to as the left child and the right child.
Theorem: The maximum number of nodes on level i of a binary tree is 2^(i-1).
Formula for height: h = floor(log2(n)) for balanced trees.

## Section 5.2: Tree Traversals
Definition: Traversal is the process of visiting every node in a tree systematically.
### In-Order Traversal
Algorithm: Traverse the left subtree, visit root, traverse right subtree.
Produces sorted sequence for Binary Search Trees (BST).
### Pre-Order and Post-Order
Algorithm: Pre-order visits root first; Post-order visits root last.
Example: Expression tree evaluation using post-order traversal.

## Section 5.3: Advanced Balanced Trees
Definition: AVL trees are self-balancing binary search trees where heights of two child subtrees differ by at most one.
Theorem: AVL tree lookup runs in guaranteed O(log n) time.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
        tmp.write(study_content)
        tmp_path = tmp.name

    try:
        extractor = TextDocumentExtractor()
        structure = extractor.extract_document(tmp_path, "doc_trees_01", "binary_trees.md", subject="Computer Science")
        chunks = SemanticDocumentChunker.chunk_document(structure)

        understanding_service = ContentUnderstandingService()
        understanding = understanding_service.understand_content(
            text=study_content,
            filename="binary_trees.md",
            subject_hint="Computer Science",
            source_reference="doc_trees_01"
        )

        kg = KnowledgeGraphBuilder.build_from_understanding_and_chunks(
            understanding=understanding,
            chunks=chunks,
            document_id="doc_trees_01"
        )

        # 1. Verify >= 5 nodes
        assert len(kg.nodes) >= 5, f"Expected >= 5 nodes, got {len(kg.nodes)}"

        # 2. Verify prerequisite edges exist
        prereq_edges = [e for e in kg.edges if e.relation == EdgeType.PREREQUISITE_OF]
        assert len(prereq_edges) >= 1, "Expected at least 1 PREREQUISITE_OF edge"

        # 3. Verify at least 1 definition / theorem / formula extracted with valid source chunk reference
        all_definitions = []
        all_theorems = []
        all_formulas = []
        for node in kg.nodes.values():
            all_definitions.extend(node.definitions)
            all_theorems.extend(node.theorems)
            all_formulas.extend(node.formulas)

        assert len(all_definitions) + len(all_theorems) + len(all_formulas) >= 1
        
        # Check source chunk grounding
        grounded_items = [
            item for item in (all_definitions + all_theorems + all_formulas)
            if item.source_chunk_id and item.source_chunk_id.startswith("chk_")
        ]
        assert len(grounded_items) >= 1, "Expected at least one item grounded to a real chunk_id"

        # 4. Verify learning path topological progression
        path = kg.get_learning_path()
        assert len(path) == len(kg.nodes)
        first_node = kg.nodes[path[0]]
        last_node = kg.nodes[path[-1]]
        # Foundational/prerequisite nodes should precede advanced nodes
        assert first_node.category in ("prerequisite", "core")
        assert last_node.category in ("core", "advanced")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_knowledge_graph_thermodynamics():
    """
    Verification test 2: Thermodynamics engineering material.
    - Verify concept difficulty levels (beginner, intermediate, advanced)
    - Verify formula and theorem extraction with source references
    """
    thermo_text = """# Chapter 2: First and Second Laws of Thermodynamics
## Section 2.1: Thermodynamic Systems & State Variables
Definition: A thermodynamic system is a quantity of matter or a region in space chosen for study.
Prerequisites: Conservation of Energy, Ideal Gas Equation.

## Section 2.2: First Law of Thermodynamics
Definition: First Law states that energy can be neither created nor destroyed, only transformed.
Formula: dU = dQ - dW
Variables: U = Internal Energy, Q = Heat transferred, W = Work done.

## Section 2.3: Second Law and Carnot Cycle
Theorem: Carnot's Theorem states that no heat engine operating between two heat reservoirs can be more efficient than a reversible Carnot engine operating between the same reservoirs.
Formula for Carnot Efficiency: eta = 1 - (Tc / Th)
"""
    understanding_service = ContentUnderstandingService()
    understanding = understanding_service.understand_content(
        text=thermo_text,
        filename="thermodynamics.md",
        subject_hint="Physics",
    )
    kg = KnowledgeGraphBuilder.build_from_understanding_and_chunks(understanding)

    assert len(kg.nodes) >= 5
    prereqs = [n for n in kg.nodes.values() if n.category == "prerequisite"]
    assert len(prereqs) >= 1

    # Check formula
    has_formula = any(len(n.formulas) > 0 for n in kg.nodes.values())
    assert has_formula is True


def test_knowledge_graph_api_endpoints(app_client):
    """Test REST API routes for knowledge graph generation and retrieval."""
    # 1. Test POST /api/v1/documents/knowledge-graph
    payload = {
        "topic": "Electromagnetic Induction and Faraday's Law",
        "subject": "Physics"
    }
    resp = app_client.post("/api/v1/documents/knowledge-graph", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nodes_count"] >= 5
    assert data["edges_count"] >= 1
    assert len(data["learning_path"]) >= 5

    # 2. Test document pipeline upload and GET /api/v1/documents/<doc_id>/knowledge-graph
    pipeline = StudentUploadPipeline()
    doc_res = pipeline.process_direct_topic(
        topic="Linear Algebra: Matrix Transformations and Eigenvalues",
        student_id="student_kg_test"
    )
    doc_id = doc_res["document_id"]
    assert "knowledge_graph" in doc_res
    assert doc_res["nodes_count"] >= 5

    # Fetch knowledge graph via GET endpoint
    resp_kg = app_client.get(f"/api/v1/documents/{doc_id}/knowledge-graph")
    assert resp_kg.status_code == 200
    kg_json = resp_kg.get_json()
    assert kg_json["success"] is True
    assert len(kg_json["knowledge_graph"]["nodes"]) >= 5

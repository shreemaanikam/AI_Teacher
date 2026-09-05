"""
Unit and Integration Tests for Content Understanding Service (Phase 1).
Validates dynamic subject classification and conceptual structuring across multiple college disciplines:
Physics, Computer Science, and Mathematics, as well as direct topic inputs.
"""

import pytest
from app import create_app
from app.rag.content_understanding import ContentUnderstandingService, CourseUnderstanding


@pytest.fixture
def service():
    return ContentUnderstandingService()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_1_computer_science_content_understanding(service):
    cs_material = """
# Data Structures & Algorithms
Chapter 4: Non-Linear Hierarchical Structures
## Binary Search Trees (BST)
A binary search tree is defined as a binary tree with the key property that every node's left subtree
has keys strictly less, and right subtree has keys strictly greater.
### Tree Traversal Algorithms
- **Inorder Traversal**: Left, Node, Right. Used to retrieve keys in non-decreasing order.
- **Preorder Traversal**: Node, Left, Right. Used to serialize and duplicate trees.
- **Postorder Traversal**: Left, Right, Node. Used for bottom-up cleanup and postfix evaluation.
### Search and Insert Operations
def bst_insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = bst_insert(root.left, val)
    else:
        root.right = bst_insert(root.right, val)
    return root
Worked Example: Inserting keys [10, 5, 15, 3, 7] into an initially empty BST.
"""
    result = service.understand_content(cs_material, filename="cs_trees_notes.md")
    assert isinstance(result, CourseUnderstanding)
    assert result.subject == "Computer Science"
    assert "Data Structures" in result.course or "Computer Science" in result.course
    assert len(result.concepts) >= 3
    concept_names = [c["name"].lower() for c in result.concepts]
    assert any("traversal" in name or "inorder" in name for name in concept_names)
    assert len(result.practical_topics) > 0


def test_2_mathematics_content_understanding(service):
    math_material = """
# Advanced College Calculus
Unit 2: Differential Calculus and Derivatives
## Definition of the Derivative
The derivative of a function f at point x is defined as the limit of the difference quotient:
Formula: f'(x) = lim(h->0) (f(x+h) - f(x)) / h
### The Power Rule
For any real exponent n: d/dx (x^n) = n * x^(n-1).
### The Chain Rule for Composite Functions
If y = f(u) and u = g(x), then dy/dx = (dy/du) * (du/dx).
Worked Example: Find the derivative of f(x) = (4x^3 - 2x + 1)^5.
Problem 1: Differentiate g(t) = sin(3t^2).
"""
    result = service.understand_content(math_material, filename="math_calculus_notes.txt")
    assert isinstance(result, CourseUnderstanding)
    assert result.subject == "Mathematics"
    assert "Calculus" in result.course or "Mathematics" in result.course
    assert len(result.concepts) >= 2
    concept_names = [c["name"].lower() for c in result.concepts]
    assert any("rule" in name or "chain" in name or "power" in name for name in concept_names)
    assert len(result.formulas) >= 1


def test_3_physics_content_understanding(service):
    physics_material = """
# University Physics II: Electromagnetism
Chapter 7: Magnetic Induction and Faraday's Law
## Magnetic Flux
Magnetic flux is defined as the surface integral of the normal component of magnetic field B.
Formula: Phi = B * A * cos(theta)
## Faraday's Law of Electromagnetic Induction
The induced electromotive force in any closed loop is proportional to the rate of change of magnetic flux.
Formula: EMF = -N * (dPhi / dt)
### Lenz's Law
The polarity of the induced emf is such that it tends to produce a current that will create a magnetic flux
to oppose the change in magnetic flux which produced it.
Worked Example: A circular wire loop with radius 0.1m is placed in a magnetic field changing at 0.5 T/s.
"""
    result = service.understand_content(physics_material, filename="physics_induction.md")
    assert isinstance(result, CourseUnderstanding)
    assert result.subject == "Physics"
    assert len(result.concepts) >= 1
    assert len(result.formulas) >= 1
    assert any("lenz" in c["name"].lower() for c in result.concepts)


def test_4_direct_topic_understanding(service):
    topic_result = service.understand_topic("Operating Systems Unit 3: Process Synchronization and Semaphores")
    assert isinstance(topic_result, CourseUnderstanding)
    assert topic_result.subject == "Computer Science"
    assert "Process Synchronization" in topic_result.topic or "Operating Systems" in topic_result.topic
    assert len(topic_result.concepts) >= 2
    assert topic_result.source_type == "direct_topic"


def test_5_rest_api_understand_endpoint(client):
    payload = {
        "text": "# Discrete Mathematics\nChapter 1: Graph Theory\n## Graph Isomorphism\nA graph isomorphism is defined as a bijection between vertex sets preserving adjacency.\n### Euler Paths and Circuits\nAn Euler path is a trail in a finite graph that visits every edge exactly once.",
        "filename": "discrete_math.md"
    }
    res = client.post("/api/v1/documents/understand", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    und = data["understanding"]
    assert und["subject"] == "Mathematics"
    assert len(und["concepts"]) >= 1

    # Test direct topic submission to the same endpoint
    topic_payload = {"topic": "Linear Algebra Matrix Inverses"}
    res_topic = client.post("/api/v1/documents/understand", json=topic_payload)
    assert res_topic.status_code == 200
    topic_data = res_topic.get_json()
    assert topic_data["success"] is True
    assert topic_data["understanding"]["subject"] == "Mathematics"

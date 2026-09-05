"""
Tests for STAGE ML-COURSE-11: Concept Graph Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.concept_graph import MLConceptGraph


class TestMLConceptGraph:
    """Test suite for prerequisite DAG, topological sorting, and acyclicity."""

    @pytest.fixture(autouse=True)
    def setup_graph(self):
        self.graph = MLConceptGraph.get_instance()

    def test_graph_has_all_55_nodes(self):
        assert len(self.graph._concepts) == 55

    def test_strictly_acyclic_zero_cycles(self):
        cycles = self.graph.detect_cycles()
        assert cycles == [], f"Found cycles in concept graph: {cycles}"

    def test_topological_sort_contains_all_55_nodes(self):
        topo = self.graph.topological_sort()
        assert len(topo) == 55
        assert len(set(topo)) == 55

        # Verify topological property: for each edge u -> v, u appears before v
        indices = {c: i for i, c in enumerate(topo)}
        for u, deps in self.graph._adj.items():
            for v in deps:
                assert indices[u] < indices[v], f"Topological violation: {u} (pos {indices[u]}) after {v} (pos {indices[v]})"

    def test_direct_and_all_prerequisites(self):
        # Backprop should depend on ANN architectures which depends on Perceptron activations
        prereqs = self.graph.get_direct_prerequisites("ml.u3.backpropagation")
        assert "ml.u3.ann_architectures" in prereqs

        all_prereqs = self.graph.get_all_prerequisites("ml.u3.backpropagation")
        assert "ml.u2.perceptron" in all_prereqs
        assert "ml.u3.ann_intro" in all_prereqs

    def test_cross_unit_bridges(self):
        bridges = self.graph.get_cross_unit_bridges()
        assert len(bridges) >= 8

        # Check bridge from Unit 1 to Unit 2
        u1_to_u2 = [b for b in bridges if b["prerequisite_unit"] == 1 and b["dependent_unit"] == 2]
        assert len(u1_to_u2) >= 3

        # Check bridge from Unit 2 to Unit 3
        u2_to_u3 = [b for b in bridges if b["prerequisite_unit"] == 2 and b["dependent_unit"] == 3]
        assert any(b["prerequisite_id"] == "ml.u2.perceptron" and b["dependent_id"] == "ml.u3.ann_intro" for b in u2_to_u3)

        # Check bridge from Unit 1 to Unit 5
        u1_to_u5 = [b for b in bridges if b["prerequisite_unit"] == 1 and b["dependent_unit"] == 5]
        assert len(u1_to_u5) >= 2

    def test_learning_path_generation(self):
        path = self.graph.get_learning_path("ml.u5.q_learning")
        assert path[-1] == "ml.u5.q_learning"
        assert "ml.u5.mdp" in path
        assert "ml.u5.reinforcement_learning" in path
        assert "ml.u1.learning_types" in path

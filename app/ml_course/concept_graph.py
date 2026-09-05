"""
STAGE ML-COURSE-11: Concept Graph Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Builds and validates the Directed Acyclic Graph (DAG) across all 55 canonical concepts,
providing topological sequencing, transitive prerequisite resolution, cross-unit bridges,
and cycle detection.
"""

from __future__ import annotations
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Any, Tuple
from app.ml_course.knowledge import CourseKnowledgeBase


class MLConceptGraph:
    """
    Pedagogical Prerequisite Graph (DAG) across the 55 Machine Learning concepts.
    Guarantees acyclicity and generates optimal adaptive learning pathways.
    """

    _instance: Optional[MLConceptGraph] = None

    def __init__(self):
        self._adj: Dict[str, Set[str]] = defaultdict(set)      # prereq -> set of dependents
        self._rev_adj: Dict[str, Set[str]] = defaultdict(set)  # concept -> set of prerequisites
        self._concepts: Set[str] = set()
        self._build_default_graph()

    @classmethod
    def get_instance(cls) -> MLConceptGraph:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_default_graph(self) -> None:
        kb = CourseKnowledgeBase.get_instance()
        self._concepts = set(kb._concepts.keys())

        # Seed the nodes in the adjacency maps
        for cid in self._concepts:
            if cid not in self._adj:
                self._adj[cid] = set()
            if cid not in self._rev_adj:
                self._rev_adj[cid] = set()

        # Dependencies definition: (prereq, dependent)
        edges: List[Tuple[str, str]] = [
            # --- UNIT I Intra-Dependencies ---
            ("ml.u1.intro", "ml.u1.learning_types"),
            ("ml.u1.learning_types", "ml.u1.hypothesis_space"),
            ("ml.u1.hypothesis_space", "ml.u1.inductive_bias"),
            ("ml.u1.train_test_split", "ml.u1.cross_validation"),
            ("ml.u1.cross_validation", "ml.u1.evaluation_metrics"),
            ("ml.u1.underfitting_overfitting", "ml.u1.bias_variance_tradeoff"),
            ("ml.u1.feature_scaling", "ml.u1.linear_regression"),
            ("ml.u1.linear_regression", "ml.u1.polynomial_regression"),

            # --- UNIT I to UNIT II Cross-Unit Bridges ---
            ("ml.u1.learning_types", "ml.u2.decision_tree"),
            ("ml.u1.learning_types", "ml.u2.knn"),
            ("ml.u1.linear_regression", "ml.u2.gradient_descent"),
            ("ml.u1.linear_regression", "ml.u2.logistic_regression"),
            ("ml.u1.linear_regression", "ml.u2.bayesian_regression"),
            ("ml.u1.hypothesis_space", "ml.u2.naive_bayes"),
            ("ml.u1.evaluation_metrics", "ml.u2.hyperparameter_tuning"),

            # --- UNIT II Intra-Dependencies ---
            ("ml.u2.decision_tree", "ml.u2.random_forest"),
            ("ml.u2.random_forest", "ml.u2.bagging_boosting"),
            ("ml.u2.gradient_descent", "ml.u2.logistic_regression"),
            ("ml.u2.perceptron", "ml.u2.svm"),
            ("ml.u2.logistic_regression", "ml.u2.perceptron"),

            # --- UNIT II to UNIT III Cross-Unit Bridges ---
            ("ml.u2.perceptron", "ml.u3.ann_intro"),
            ("ml.u3.ann_intro", "ml.u3.perceptron_activations"),
            ("ml.u3.perceptron_activations", "ml.u3.ann_architectures"),
            ("ml.u3.ann_architectures", "ml.u3.backpropagation"),
            ("ml.u3.backpropagation", "ml.u3.ann_challenges"),

            # --- UNIT III Intra-Dependencies ---
            ("ml.u3.ann_challenges", "ml.u3.cnn"),
            ("ml.u3.ann_challenges", "ml.u3.rnn"),
            ("ml.u3.rnn", "ml.u3.lstm"),
            ("ml.u3.ann_challenges", "ml.u3.generative_models"),
            ("ml.u3.generative_models", "ml.u3.gans"),
            ("ml.u3.lstm", "ml.u3.bert"),

            # --- UNIT I / UNIT II to UNIT IV Cross-Unit Bridges ---
            ("ml.u1.learning_types", "ml.u4.unsupervised_intro"),
            ("ml.u4.unsupervised_intro", "ml.u4.kmeans"),
            ("ml.u4.kmeans", "ml.u4.kmedoids"),
            ("ml.u4.kmeans", "ml.u4.hierarchical_clustering"),
            ("ml.u4.kmeans", "ml.u4.cluster_evaluation"),
            ("ml.u4.kmeans", "ml.u4.gmm"),
            ("ml.u4.gmm", "ml.u4.em_algorithm"),
            ("ml.u1.feature_scaling", "ml.u4.pca"),
            ("ml.u4.pca", "ml.u4.lda"),
            ("ml.u4.pca", "ml.u4.tsne"),
            ("ml.u4.cluster_evaluation", "ml.u4.anomaly_detection"),

            # --- UNIT I / UNIT II to UNIT V Cross-Unit Bridges ---
            ("ml.u1.linear_regression", "ml.u5.least_squares"),
            ("ml.u5.least_squares", "ml.u5.conjugate_gradient"),
            ("ml.u1.learning_types", "ml.u5.reinforcement_learning"),
            ("ml.u5.reinforcement_learning", "ml.u5.mdp"),
            ("ml.u5.mdp", "ml.u5.q_learning"),
            ("ml.u5.q_learning", "ml.u5.exploration_exploitation"),
            ("ml.u1.evaluation_metrics", "ml.u5.responsible_ai"),
            ("ml.u5.responsible_ai", "ml.u5.shap_and_lime"),
            ("ml.u1.cross_validation", "ml.u5.mlops"),
            ("ml.u5.mlops", "ml.u5.federated_learning"),
        ]

        for prereq, dep in edges:
            self.add_edge(prereq, dep)

    def add_edge(self, prereq_id: str, concept_id: str) -> None:
        if prereq_id not in self._concepts or concept_id not in self._concepts:
            raise ValueError(f"Invalid concept IDs: {prereq_id}, {concept_id}")
        self._adj[prereq_id].add(concept_id)
        self._rev_adj[concept_id].add(prereq_id)

    def get_direct_prerequisites(self, concept_id: str) -> List[str]:
        return sorted(list(self._rev_adj.get(concept_id, set())))

    def get_all_prerequisites(self, concept_id: str) -> List[str]:
        """Return all transitive prerequisites in topological order."""
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(node: str):
            for prereq in self._rev_adj.get(node, set()):
                if prereq not in visited:
                    visited.add(prereq)
                    dfs(prereq)
                    order.append(prereq)

        dfs(concept_id)
        return order

    def get_direct_dependents(self, concept_id: str) -> List[str]:
        return sorted(list(self._adj.get(concept_id, set())))

    def get_all_dependents(self, concept_id: str) -> List[str]:
        """Return all concepts that depend directly or indirectly on this concept."""
        visited: Set[str] = set()
        queue = deque([concept_id])
        while queue:
            curr = queue.popleft()
            for dep in self._adj.get(curr, set()):
                if dep not in visited:
                    visited.add(dep)
                    queue.append(dep)
        return sorted(list(visited))

    def detect_cycles(self) -> List[List[str]]:
        """Detect any directed cycles using Tarjan/DFS."""
        visited: Dict[str, int] = {c: 0 for c in self._concepts}  # 0: unvisited, 1: visiting, 2: visited
        cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(u: str):
            visited[u] = 1
            path.append(u)
            for v in self._adj.get(u, set()):
                if visited[v] == 1:
                    cycle_start = path.index(v)
                    cycles.append(path[cycle_start:] + [v])
                elif visited[v] == 0:
                    dfs(v)
            path.pop()
            visited[u] = 2

        for c in self._concepts:
            if visited[c] == 0:
                dfs(c)

        return cycles

    def topological_sort(self) -> List[str]:
        """Return a valid linear ordering of all concepts satisfying all prerequisite edges."""
        in_degree = {c: len(self._rev_adj.get(c, set())) for c in self._concepts}
        queue = deque([c for c in self._concepts if in_degree[c] == 0])
        result = []

        while queue:
            # Sort queue for deterministic ordering
            u = queue.popleft()
            result.append(u)
            for v in sorted(list(self._adj.get(u, set()))):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(result) != len(self._concepts):
            cycles = self.detect_cycles()
            raise ValueError(f"Graph contains cycles: {cycles}")

        return result

    def get_learning_path(self, target_concept_id: str) -> List[str]:
        """Generate the minimal prerequisite learning sequence leading up to target_concept_id."""
        if target_concept_id not in self._concepts:
            raise ValueError(f"Unknown concept ID: {target_concept_id}")
        prereqs = self.get_all_prerequisites(target_concept_id)
        return prereqs + [target_concept_id]

    def get_cross_unit_bridges(self) -> List[Dict[str, Any]]:
        """Retrieve all prerequisite edges that span across different units."""
        kb = CourseKnowledgeBase.get_instance()
        bridges = []
        for prereq, dependents in self._adj.items():
            u_prereq = kb.get_concept(prereq).unit_number
            for dep in dependents:
                u_dep = kb.get_concept(dep).unit_number
                if u_prereq != u_dep:
                    bridges.append({
                        "prerequisite_id": prereq,
                        "prerequisite_unit": u_prereq,
                        "dependent_id": dep,
                        "dependent_unit": u_dep,
                    })
        return bridges

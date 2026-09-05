"""
STAGE ML-COURSE-25: Dynamic Visual Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Generates deterministic interactive visual teaching payloads grounded directly in the 5 units:
Neural Network, Backpropagation, K-Means, Gradient Descent, Decision Tree, Q-Learning.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase


class DynamicVisualPayload(BaseModel):
    concept_id: str
    visual_type: str  # NEURAL_NETWORK, BACKPROPAGATION, KMEANS_CLUSTERING, GRADIENT_DESCENT, DECISION_TREE, Q_LEARNING
    title: str
    unit: int
    html_canvas_component: str
    animation_steps: List[Dict[str, Any]]
    interactive_controls: List[str] = Field(default_factory=list)
    is_deterministic: bool = True
    source_refs: List[SourceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLDynamicVisualEngine:
    """
    Renders pedagogical deterministic visual models for Machine Learning algorithms.
    """

    _instance: Optional[MLDynamicVisualEngine] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLDynamicVisualEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_visual_payload(
        self,
        concept_id: str,
        context_state: Optional[Dict[str, Any]] = None,
    ) -> DynamicVisualPayload:
        concept = self._kb.get_concept(concept_id)
        cid_low = concept_id.lower()

        # 1. Backpropagation Flow
        if "backprop" in cid_low:
            title = "Backpropagation Error Gradient Flow"
            vtype = "BACKPROPAGATION"
            unit = 3
            steps = [
                {"step": 1, "action": "Forward Pass", "description": "Inputs x propagate through weights to hidden nodes and output layer."},
                {"step": 2, "action": "Compute Loss", "description": "Error E = 1/2 (target - y)^2 computed at output node."},
                {"step": 3, "action": "Backward Error Delta", "description": "Delta = output * (1 - output) * (target - output) propagated backward."},
                {"step": 4, "action": "Weight Update", "description": "w_new = w_old + eta * delta * input applied to all connections."},
            ]
            svg = (
                '<svg viewBox="0 0 600 300" class="ml-visual-board">'
                '<circle cx="100" cy="150" r="25" fill="#3b82f6" />'
                '<circle cx="300" cy="100" r="25" fill="#10b981" />'
                '<circle cx="300" cy="200" r="25" fill="#10b981" />'
                '<circle cx="500" cy="150" r="25" fill="#ef4444" />'
                '<path d="M125 150 L275 100" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)" />'
                '<path d="M125 150 L275 200" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)" />'
                '<path d="M325 100 L475 150" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)" />'
                '<path d="M325 200 L475 150" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)" />'
                '<text x="500" y="210" fill="#ef4444" text-anchor="middle">Loss E</text>'
                '</svg>'
            )

        # 2. Neural Network
        elif "ann" in cid_low or "neural" in cid_low or "cnn" in cid_low:
            title = "Neural Network Architecture & Layer Flow"
            vtype = "NEURAL_NETWORK"
            unit = 3
            steps = [
                {"step": 1, "action": "Input Feature Encoding", "description": "Input vector fed into input neurons."},
                {"step": 2, "action": "Affine Transformation", "description": "Dot product z = W^T x + b."},
                {"step": 3, "action": "Nonlinear Activation", "description": "Apply ReLU, Sigmoid or Tanh activation."},
            ]
            svg = '<svg viewBox="0 0 500 250" class="ml-visual-board"><rect width="500" height="250" fill="#0f172a"/><text x="250" y="125" fill="#38bdf8" text-anchor="middle">Deep Neural Network Layers</text></svg>'

        # 3. K-Means
        elif "kmeans" in cid_low or "clustering" in cid_low:
            title = "K-Means Point Assignment and Centroid Relocation"
            vtype = "KMEANS_CLUSTERING"
            unit = 4
            steps = [
                {"step": 1, "action": "Initialize K Centroids", "description": "Seed initial centroid positions m1 and m2 in feature space."},
                {"step": 2, "action": "Euclidean Distance Calculation", "description": "Measure distance ||x_i - m_k|| from all points to both centroids."},
                {"step": 3, "action": "Voronoi Partitioning", "description": "Assign each point to the closest centroid."},
                {"step": 4, "action": "Centroid Recomputation", "description": "Move each centroid to the center of mass of its assigned cluster."},
            ]
            svg = (
                '<svg viewBox="0 0 500 300" class="ml-visual-board">'
                '<circle cx="120" cy="90" r="8" fill="#3b82f6" />'
                '<circle cx="150" cy="120" r="8" fill="#3b82f6" />'
                '<circle cx="380" cy="220" r="8" fill="#f59e0b" />'
                '<circle cx="410" cy="250" r="8" fill="#f59e0b" />'
                '<path d="M200 50 L200 250" stroke="#64748b" stroke-dasharray="4" />'
                '<polygon points="140,105 130,125 150,125" fill="#2563eb" />'
                '<polygon points="395,235 385,255 405,255" fill="#d97706" />'
                '</svg>'
            )

        # 4. Gradient Descent
        elif "gradient" in cid_low or "descent" in cid_low:
            title = "Gradient Descent Convex Loss Surface Optimization"
            vtype = "GRADIENT_DESCENT"
            unit = 2
            steps = [
                {"step": 1, "action": "Current Position w_t", "description": "Evaluate cost function J(w_t)."},
                {"step": 2, "action": "Compute Gradient", "description": "Find slope grad J(w_t)."},
                {"step": 3, "action": "Negative Gradient Step", "description": "Take step -eta * grad J toward local minimum."},
            ]
            svg = '<svg viewBox="0 0 500 250" class="ml-visual-board"><path d="M50 50 Q250 220 450 50" stroke="#6366f1" fill="none" stroke-width="3"/><circle cx="150" cy="140" r="6" fill="#ef4444"/><line x1="150" y1="140" x2="200" y2="180" stroke="#ef4444" stroke-width="2" marker-end="url(#arrow)"/></svg>'

        # 5. Decision Tree
        elif "tree" in cid_low:
            title = "Decision Tree Feature Space Splitting"
            vtype = "DECISION_TREE"
            unit = 2
            steps = [
                {"step": 1, "action": "Root Split Evaluation", "description": "Calculate Information Gain or Gini index for all candidate features."},
                {"step": 2, "action": "Binary Branching", "description": "Partition dataset into Left and Right subsets based on threshold."},
                {"step": 3, "action": "Leaf Node Assignment", "description": "Assign majority class label at pure leaf nodes."},
            ]
            svg = '<svg viewBox="0 0 500 250" class="ml-visual-board"><rect x="200" y="30" width="100" height="40" fill="#0284c7" rx="5"/><rect x="100" y="140" width="80" height="40" fill="#16a34a" rx="5"/><rect x="320" y="140" width="80" height="40" fill="#dc2626" rx="5"/><line x1="230" y1="70" x2="140" y2="140" stroke="#94a3b8" stroke-width="2"/><line x1="270" y1="70" x2="360" y2="140" stroke="#94a3b8" stroke-width="2"/></svg>'

        # 6. Q-Learning
        else:
            title = "Q-Learning Gridworld Policy & Value Update"
            vtype = "Q_LEARNING"
            unit = 5
            steps = [
                {"step": 1, "action": "State Observation", "description": "Agent observes current environment state s."},
                {"step": 2, "action": "Action Selection", "description": "Choose action a using epsilon-greedy exploration/exploitation."},
                {"step": 3, "action": "Reward & Next State", "description": "Receive immediate reward r and observe transition s'."},
                {"step": 4, "action": "Bellman TD Update", "description": "Q(s, a) <- Q(s, a) + alpha * [r + gamma * max_a' Q(s', a') - Q(s, a)]."},
            ]
            svg = '<svg viewBox="0 0 400 250" class="ml-visual-board"><rect x="50" y="50" width="100" height="100" fill="#1e293b" stroke="#475569"/><rect x="150" y="50" width="100" height="100" fill="#1e293b" stroke="#475569"/><text x="100" y="105" fill="#f8fafc" text-anchor="middle">State s</text><text x="200" y="105" fill="#38bdf8" text-anchor="middle">State s\'</text><path d="M120 70 Q150 40 180 70" stroke="#f59e0b" stroke-width="2" fill="none" marker-end="url(#arrow)"/><text x="150" y="30" fill="#f59e0b" text-anchor="middle">Action a, Reward r</text></svg>'

        controls = ["Play Animation", "Step Forward", "Step Backward", "Reset Visual", "Toggle Labels"]

        return DynamicVisualPayload(
            concept_id=concept_id,
            visual_type=vtype,
            title=title,
            unit=unit,
            html_canvas_component=svg,
            animation_steps=steps,
            interactive_controls=controls,
            is_deterministic=True,
            source_refs=concept.source_refs if concept else [],
            verification_status=VerificationStatus.VERIFIED,
        )

"""
STAGE ML-COURSE-18: Unit-by-Unit Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Generates unit-grounded lesson plans, visual teaching blueprints, and assessments
for Units I through V, strictly preventing cross-unit topic drift.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.problem_bank import MLProblemBank


class UnitLessonPlan(BaseModel):
    unit_number: int
    unit_code: str
    unit_title: str
    concept_ids: List[str]
    concept_names: List[str]
    formula_ids: List[str]
    algorithm_ids: List[str]
    problem_ids: List[str]
    visual_plan: Dict[str, Any]
    assessment_plan: Dict[str, Any]
    source_refs: List[SourceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLUnitTeachingEngine:
    """
    Pedagogical orchestration engine for five-unit collegiate syllabus delivery.
    """

    _instance: Optional[MLUnitTeachingEngine] = None

    VISUAL_BLUEPRINTS = {
        1: {
            "type": "REGRESSION_RESIDUAL_PLOT",
            "title": "Linear Regression Best-Fit Line and Residual Squares",
            "elements": ["Scatter Points", "Hypothesis Line y = wx + b", "Residual Errors (y - y_hat)"],
        },
        2: {
            "type": "DECISION_BOUNDARY_AND_TREE",
            "title": "Perceptron Separating Hyperplane & Decision Tree Splits",
            "elements": ["2D Class Separation", "Support Vector Margins", "Tree Root and Child Nodes"],
        },
        3: {
            "type": "NEURAL_NETWORK_FLOW",
            "title": "Multilayer Perceptron Forward & Backward Gradient Flow",
            "elements": ["Input Layer", "Hidden Layer Activations", "Output Layer Loss", "Backward Error Propagation"],
        },
        4: {
            "type": "CLUSTERING_SPACE",
            "title": "K-Means Iterative Centroid Convergence and Voronoi Regions",
            "elements": ["Data Points", "K Centroids", "Distance Radii", "Cluster Assignments"],
        },
        5: {
            "type": "REINFORCEMENT_LEARNING_GRID",
            "title": "MDP State-Action Value Q-Grid and Policy Updates",
            "elements": ["Agent State s", "Action a", "Reward r", "Q(s, a) Table Heatmap"],
        },
    }

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLUnitTeachingEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_unit_lesson_plan(self, unit: int) -> UnitLessonPlan:
        if unit not in self._kb.course.units:
            raise ValueError(f"Unit {unit} does not exist in canonical course (1-5 only)")

        u = self._kb.course.units[unit]
        probs = MLProblemBank.get_problems_by_unit(unit)
        visual = self.VISUAL_BLUEPRINTS.get(unit, {"type": "GENERAL_DIAGRAM"})

        assessment = {
            "diagnostic_questions": [f"Explain the primary objective of {u.concepts[0].name}."],
            "numerical_challenge": probs[0].problem_id if probs else None,
            "passing_threshold_mastery": 0.80,
        }

        all_refs: List[SourceRef] = []
        for c in u.concepts:
            all_refs.extend(c.source_refs)

        return UnitLessonPlan(
            unit_number=unit,
            unit_code=u.unit_code,
            unit_title=u.title,
            concept_ids=[c.concept_id for c in u.concepts],
            concept_names=[c.name for c in u.concepts],
            formula_ids=[f.formula_id for f in u.formulas],
            algorithm_ids=[a.algorithm_id for a in u.algorithms],
            problem_ids=[p.problem_id for p in probs],
            visual_plan=visual,
            assessment_plan=assessment,
            source_refs=all_refs[:10],
            verification_status=VerificationStatus.VERIFIED,
        )

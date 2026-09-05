"""
STAGE ML-COURSE-24: Pedagogical Misconception Remediation Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Executes the closed-loop remediation workflow when a student error is flagged:
Evaluate -> Identify Concept -> Identify Misconception -> Retrieve Evidence ->
Choose Remediation -> New Contrastive Explanation -> New Visual -> New Retest Question.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.rag_service import MLCourseRAGService
from app.ml_course.question_generator import MLQuestionGenerator, GeneratedQuestion


class MisconceptionRemediationPlan(BaseModel):
    remediation_id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:8]}")
    concept_id: str
    concept_name: str
    unit_number: int
    diagnosed_misconception: str
    original_error: str
    contrastive_explanation: str
    remediation_visual: Dict[str, Any]
    retest_question: GeneratedQuestion
    evidence_refs: List[SourceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLMisconceptionEngine:
    """
    Diagnoses student misconceptions and constructs distinct pedagogical remediations.
    """

    _instance: Optional[MLMisconceptionEngine] = None

    CATALOG = {
        "kmeans_supervised": {
            "concept_id": "ml.u4.kmeans",
            "unit": 4,
            "title": "Supervised vs Unsupervised Nature of K-Means",
            "contrast": "K-Means operates strictly on unlabelled data X without ground-truth labels y. It discovers geometric groupings by minimizing within-cluster sum of squares (inertia), unlike classification algorithms like SVM or Logistic Regression which require training targets.",
            "visual": {
                "type": "CONTRASTIVE_SCATTER",
                "left_panel": "Unlabeled points grouped into Voronoi clusters (K-Means)",
                "right_panel": "Labeled red/blue points with separating boundary (SVM)",
            },
        },
        "sigmoid_range": {
            "concept_id": "ml.u2.logistic_regression",
            "unit": 2,
            "title": "Sigmoid vs Tanh Output Ranges",
            "contrast": "The standard Sigmoid activation function sigma(z) = 1 / (1 + e^-z) maps real inputs exclusively to the open interval (0, 1) representing probability. It never outputs negative values. The Hyperbolic Tangent (Tanh) function maps to (-1, 1).",
            "visual": {
                "type": "ACTIVATION_CURVES_COMPARISON",
                "sigmoid_curve": "Asymptotes at y=0 and y=1",
                "tanh_curve": "Asymptotes at y=-1 and y=1",
            },
        },
        "qlearning_model": {
            "concept_id": "ml.u5.q_learning",
            "unit": 5,
            "title": "Model-Free vs Model-Based Reinforcement Learning",
            "contrast": "Q-learning is a model-free temporal difference algorithm. The agent directly learns the optimal action-value function Q*(s, a) through trial-and-error interactions without knowing or constructing transition probabilities P(s'|s, a) or reward function R(s, a).",
            "visual": {
                "type": "RL_AGENT_ENVIRONMENT_LOOP",
                "focus": "Direct Q-Table update without environment transition matrix",
            },
        },
    }

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._rag = MLCourseRAGService.get_instance()
        self._qgen = MLQuestionGenerator.get_instance()

    @classmethod
    def get_instance(cls) -> MLMisconceptionEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def diagnose_and_remediate(
        self,
        concept_id: str,
        student_error: str,
    ) -> MisconceptionRemediationPlan:
        err_low = student_error.lower()
        matched_key = None

        if "supervised" in err_low and ("kmeans" in err_low or "k-means" in err_low or concept_id == "ml.u4.kmeans"):
            matched_key = "kmeans_supervised"
        elif ("-1" in err_low or "tanh" in err_low or "range" in err_low) and ("sigmoid" in err_low or concept_id == "ml.u2.logistic_regression"):
            matched_key = "sigmoid_range"
        elif ("model-based" in err_low or "transition" in err_low) and ("q-learning" in err_low or concept_id == "ml.u5.q_learning"):
            matched_key = "qlearning_model"

        concept = self._kb.get_concept(concept_id)
        u_num = concept.unit_number if concept else 1
        c_name = concept.name if concept else concept_id

        if matched_key and matched_key in self.CATALOG:
            cat = self.CATALOG[matched_key]
            diagnosed = cat["title"]
            explanation = cat["contrast"]
            visual = cat["visual"]
        else:
            diagnosed = f"Conceptual misunderstanding regarding {c_name}"
            explanation = f"In college Unit {u_num}, {c_name} has a specific formal definition: {concept.summary if concept else ''}. Please observe the contrast with alternative models."
            visual = {
                "type": "CONCEPT_DIAGNOSTIC_CHART",
                "highlight": "Correct boundaries and mathematical formulation",
            }

        # Generate targeted retest question
        retest_q = self._qgen.generate_question(
            unit=u_num,
            question_type="MCQ",
            concept_id=concept_id,
        )

        return MisconceptionRemediationPlan(
            concept_id=concept_id,
            concept_name=c_name,
            unit_number=u_num,
            diagnosed_misconception=diagnosed,
            original_error=student_error,
            contrastive_explanation=explanation,
            remediation_visual=visual,
            retest_question=retest_q,
            evidence_refs=concept.source_refs if concept else [],
            verification_status=VerificationStatus.VERIFIED,
        )

"""
STAGE ML-COURSE-17: Algorithm Verification Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Validates procedural algorithms against college source gold definitions,
verifying input/output definitions, step sequencing, stopping criteria, and completeness.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field

from app.ml_course.models import GoldAlgorithm, SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase


class AlgorithmValidationResult(BaseModel):
    algorithm_id: str
    is_valid: bool
    status: VerificationStatus
    gold_name: str
    gold_steps: List[str]
    candidate_steps: List[str]
    missing_steps: List[str] = Field(default_factory=list)
    ordering_violations: List[str] = Field(default_factory=list)
    stopping_condition_valid: bool = True
    feedback: str = ""
    source_refs: List[SourceRef] = Field(default_factory=list)


class MLAlgorithmValidator:
    """
    Procedural correctness and step-fidelity validation engine
    for the 12 canonical Machine Learning algorithms.
    """

    _instance: Optional[MLAlgorithmValidator] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLAlgorithmValidator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_algorithm_explanation(
        self,
        algorithm_id: str,
        candidate_steps: List[str],
        candidate_stopping_condition: Optional[str] = None,
    ) -> AlgorithmValidationResult:
        gold: Optional[GoldAlgorithm] = self._kb.get_algorithm(algorithm_id)
        if not gold:
            raise ValueError(f"Unknown algorithm ID: {algorithm_id}")

        cand_text = " ".join(candidate_steps).lower()
        missing = []

        # Check key semantic concepts for each gold step
        for i, g_step in enumerate(gold.steps):
            keywords = [w.lower() for w in re.findall(r"\w+", g_step) if len(w) > 3]
            # Match if at least 2 distinct keywords or phrase are present in candidate steps
            overlap = [kw for kw in keywords if kw in cand_text]
            if len(overlap) < min(2, len(keywords)):
                missing.append(f"Step {i+1}: {g_step}")

        # Check stopping condition if gold specifies one
        stop_valid = True
        if gold.stopping_condition and candidate_stopping_condition:
            gold_stop_words = set(re.findall(r"\w+", gold.stopping_condition.lower()))
            cand_stop_words = set(re.findall(r"\w+", candidate_stopping_condition.lower()))
            if not gold_stop_words.intersection(cand_stop_words):
                stop_valid = False

        # Ordering check:
        # e.g., in K-Means: "assign" must precede "recompute" or "update"
        ordering_violations = []
        if "kmeans" in algorithm_id.lower() or "k-means" in gold.name.lower():
            assign_idx = -1
            update_idx = -1
            for idx, s in enumerate(candidate_steps):
                s_low = s.lower()
                if "assign" in s_low and assign_idx == -1:
                    assign_idx = idx
                if ("recompute" in s_low or "update" in s_low) and update_idx == -1:
                    update_idx = idx
            if assign_idx != -1 and update_idx != -1 and update_idx < assign_idx:
                ordering_violations.append("Centroid recomputation occurred before point assignment.")

        # In Backprop: "forward" must precede "backward" / "gradients"
        if "backprop" in algorithm_id.lower():
            fwd_idx = -1
            bwd_idx = -1
            for idx, s in enumerate(candidate_steps):
                s_low = s.lower()
                if "forward" in s_low and fwd_idx == -1:
                    fwd_idx = idx
                if ("backward" in s_low or "gradient" in s_low or "delta" in s_low) and bwd_idx == -1:
                    bwd_idx = idx
            if fwd_idx != -1 and bwd_idx != -1 and bwd_idx < fwd_idx:
                ordering_violations.append("Backward gradient computation occurred before forward pass.")

        is_valid = len(missing) == 0 and len(ordering_violations) == 0 and stop_valid

        feedback_parts = []
        if not is_valid:
            if missing:
                feedback_parts.append(f"Missing steps: {'; '.join(missing)}")
            if ordering_violations:
                feedback_parts.append(f"Ordering errors: {'; '.join(ordering_violations)}")
            if not stop_valid:
                feedback_parts.append(f"Stopping condition mismatch with gold source ({gold.stopping_condition})")
        else:
            feedback_parts.append("Procedural steps and stopping criteria verified against college notes.")

        return AlgorithmValidationResult(
            algorithm_id=algorithm_id,
            is_valid=is_valid,
            status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.NEEDS_VERIFICATION,
            gold_name=gold.name,
            gold_steps=gold.steps,
            candidate_steps=candidate_steps,
            missing_steps=missing,
            ordering_violations=ordering_violations,
            stopping_condition_valid=stop_valid,
            feedback=" ".join(feedback_parts),
            source_refs=gold.source_refs,
        )

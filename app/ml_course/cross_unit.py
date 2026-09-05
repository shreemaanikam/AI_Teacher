"""
STAGE ML-COURSE-29: Cross-Unit Synthesis & Multi-Unit Query Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Handles queries that span multiple units (e.g. Perceptron in Unit 2 vs Backprop in Unit 3;
PCA in Unit 4 with Linear Regression in Unit 1; Supervised vs Unsupervised vs RL across Units 1, 2, 4, 5).
Ensures evidence is retrieved from each involved unit without forcing single-unit lock-in.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from app.rag.models import EvidenceItem, EvidencePackage
from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.concept_graph import MLConceptGraph
from app.ml_course.rag_service import MLCourseRAGService
from app.ml_course.claim_validator import MLClaimValidator


class UnitEvidenceGroup(BaseModel):
    unit_number: int
    unit_title: str
    concepts_referenced: List[str] = Field(default_factory=list)
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    source_documents: List[str] = Field(default_factory=list)


class CrossUnitSynthesisResult(BaseModel):
    query: str
    is_cross_unit: bool
    units_involved: List[int] = Field(default_factory=list)
    unit_evidence_groups: Dict[int, UnitEvidenceGroup] = Field(default_factory=dict)
    comparative_synthesis: str
    cross_unit_bridges: List[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLCrossUnitEngine:
    """
    Coordinates multi-unit discovery, cross-unit RAG retrieval,
    and comparative conceptual synthesis across the 5 units.
    """

    _instance: Optional[MLCrossUnitEngine] = None

    # Known cross-unit bridge themes
    UNIT_TOPIC_MAP: Dict[str, int] = {
        "linear regression": 1,
        "polynomial regression": 1,
        "bias-variance": 1,
        "train test split": 1,
        "cross validation": 1,
        "perceptron": 2,
        "decision tree": 2,
        "logistic regression": 2,
        "support vector machine": 2,
        "svm": 2,
        "knn": 2,
        "naive bayes": 2,
        "gradient descent": 2,
        "neural network": 3,
        "ann": 3,
        "backpropagation": 3,
        "cnn": 3,
        "rnn": 3,
        "lstm": 3,
        "deep learning": 3,
        "unsupervised": 4,
        "k-means": 4,
        "kmeans": 4,
        "hierarchical clustering": 4,
        "pca": 4,
        "dimensionality reduction": 4,
        "em algorithm": 4,
        "reinforcement learning": 5,
        "rl": 5,
        "q-learning": 5,
        "mdp": 5,
        "least squares": 5,
        "conjugate gradient": 5,
        "mlops": 5,
    }

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._rag = MLCourseRAGService.get_instance()
        self._graph = MLConceptGraph.get_instance()
        self._validator = MLClaimValidator.get_instance()

    @classmethod
    def get_instance(cls) -> MLCrossUnitEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def detect_units(self, query: str) -> List[int]:
        """Detects which units are implicated by the query."""
        q_lower = query.lower()
        detected: Set[int] = set()

        for topic, unit in self.UNIT_TOPIC_MAP.items():
            if re.search(rf"\b{re.escape(topic)}\b", q_lower):
                detected.add(unit)

        # Check explicit unit numbers mentioned
        for u, roman in [(1, "i"), (2, "ii"), (3, "iii"), (4, "iv"), (5, "v")]:
            if f"unit {u}" in q_lower or f"unit-{roman}" in q_lower or f"unit {roman}" in q_lower:
                detected.add(u)

        return sorted(list(detected))

    def answer_cross_unit_query(
        self,
        query: str,
    ) -> CrossUnitSynthesisResult:
        """
        Retrieves evidence across each detected unit and performs structured comparative synthesis.
        """
        units = self.detect_units(query)
        if len(units) <= 1:
            # Fallback to single unit or general RAG if only one unit or none detected
            single_unit = units[0] if units else None
            pkg = self._rag.retrieve_package(query, unit=single_unit, top_k=4)
            unit_num = single_unit or 1
            unit_group = UnitEvidenceGroup(
                unit_number=unit_num,
                unit_title=self._kb.course.units[unit_num].title,
                concepts_referenced=[pkg.target_concept],
                evidence_items=pkg.evidence_items,
                source_documents=pkg.source_documents,
            )
            return CrossUnitSynthesisResult(
                query=query,
                is_cross_unit=False,
                units_involved=units,
                unit_evidence_groups={unit_num: unit_group},
                comparative_synthesis=pkg.combined_context,
                cross_unit_bridges=[],
                verification_status=VerificationStatus.VERIFIED,
            )

        # Multi-unit processing
        evidence_groups: Dict[int, UnitEvidenceGroup] = {}
        all_bridges: List[str] = []

        for u in units:
            unit_model = self._kb.course.units[u]
            # Retrieve evidence specifically for this unit's angle of the query
            unit_evidence = self._rag.retrieve(query, unit=u, top_k=3, allow_cross_unit=False)
            docs = list({item.document_id for item in unit_evidence})
            concepts = list({item.chapter for item in unit_evidence})

            evidence_groups[u] = UnitEvidenceGroup(
                unit_number=u,
                unit_title=unit_model.title,
                concepts_referenced=concepts,
                evidence_items=unit_evidence,
                source_documents=docs,
            )

        # Query concept graph for cross-unit bridge edges
        for u, dependents in self._graph._adj.items():
            for v in dependents:
                src_concept = self._kb.get_concept(u)
                tgt_concept = self._kb.get_concept(v)
                if src_concept and tgt_concept:
                    if src_concept.unit_number in units and tgt_concept.unit_number in units:
                        if src_concept.unit_number != tgt_concept.unit_number:
                            all_bridges.append(
                                f"Unit {src_concept.unit_number} ({src_concept.name}) -> PREREQUISITE -> Unit {tgt_concept.unit_number} ({tgt_concept.name})"
                            )

        # Build collegiate comparative synthesis text
        synthesis_lines = [
            f"Cross-Unit Synthesis for inquiry: '{query}'",
            f"Involves Units: {', '.join([f'Unit {u}' for u in units])}.\n",
        ]
        for u in units:
            grp = evidence_groups[u]
            synthesis_lines.append(f"--- Unit {u}: {grp.unit_title} ---")
            for it in grp.evidence_items[:2]:
                synthesis_lines.append(f"- [p.{it.page}] {it.excerpt[:180]}...")
            synthesis_lines.append("")

        if all_bridges:
            synthesis_lines.append("--- Pedagogical Dependency Bridges ---")
            for b in all_bridges[:4]:
                synthesis_lines.append(f"• {b}")

        synthesis_text = "\n".join(synthesis_lines)

        return CrossUnitSynthesisResult(
            query=query,
            is_cross_unit=True,
            units_involved=units,
            unit_evidence_groups=evidence_groups,
            comparative_synthesis=synthesis_text,
            cross_unit_bridges=all_bridges,
            verification_status=VerificationStatus.VERIFIED,
        )

"""
STAGE ML-COURSE-28: Out-of-Syllabus Detection & External Knowledge Gate Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Strict invariants:
1. Detect queries that fall outside the 5-unit college curriculum.
2. Clearly reply 'NOT FOUND IN COURSE MATERIAL' for ungrounded queries by default.
3. Only provide external knowledge when explicitly requested, and strictly label it
   with 'EXTERNAL_GENERAL_KNOWLEDGE (NOT IN COLLEGE SYLLABUS)'.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.rag_service import MLCourseRAGService


class SyllabusAssessment(BaseModel):
    query: str
    is_in_syllabus: bool
    matched_unit: Optional[int] = None
    matched_concepts: List[str] = Field(default_factory=list)
    verdict: str  # "IN_SYLLABUS", "NOT_FOUND_IN_COURSE_MATERIAL"
    response_text: str
    is_external_knowledge: bool = False
    source_label: str = "COLLEGE_COURSE_MATERIAL"
    source_refs: List[SourceRef] = Field(default_factory=list)


class MLOutOfSyllabusEngine:
    """
    Guards curriculum boundaries for AD5305 / CS4403.
    Prevents hallucinating external ML topics into the student's college syllabus.
    """

    _instance: Optional[MLOutOfSyllabusEngine] = None

    # Recognized out-of-syllabus keywords / domains
    KNOWN_OUT_OF_SYLLABUS_DOMAINS = [
        "quantum",
        "quantum machine learning",
        "qml",
        "blockchain",
        "bitcoin",
        "cryptocurrency",
        "diffusion model",
        "stable diffusion",
        "alphafold",
        "crispr",
        "genomics",
        "neuro-symbolic",
        "robotics kinematics",
        "web scraping",
        "sql injection",
    ]

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._rag = MLCourseRAGService.get_instance()

    @classmethod
    def get_instance(cls) -> MLOutOfSyllabusEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate_query(
        self,
        query: str,
        allow_general_knowledge: bool = False,
    ) -> SyllabusAssessment:
        q_lower = query.lower().strip()

        # 1. Direct check against known out-of-syllabus domains
        for domain in self.KNOWN_OUT_OF_SYLLABUS_DOMAINS:
            if domain in q_lower:
                return self._handle_out_of_syllabus(query, reason=domain, allow_general=allow_general_knowledge)

        # 2. Check knowledge base and RAG retrieval
        kb_matches = self._kb.query_by_topic(query)
        rag_matches = self._rag.retrieve(query, top_k=3)

        if kb_matches or (rag_matches and rag_matches[0].relevance_score > 0.4):
            # Topic is grounded in college syllabus
            unit = None
            concepts = []
            source_refs = []

            if kb_matches:
                unit = kb_matches[0].get("unit")
                concepts = [m.get("title", "") for m in kb_matches]
                for m in kb_matches:
                    for src in m.get("sources", []):
                        source_refs.append(SourceRef(**src))

            if not unit and rag_matches:
                # Infer unit from chapter, chunk_id, or metadata
                cid = (rag_matches[0].chunk_id or "").lower()
                chapter_str = (rag_matches[0].chapter or "").lower()
                for u, roman in [(1, "i"), (2, "ii"), (3, "iii"), (4, "iv"), (5, "v")]:
                    if (
                        f".u{u}." in cid
                        or f"unit {u}" in chapter_str
                        or f"unit-{roman}" in chapter_str
                        or f"unit {roman}" in chapter_str
                    ):
                        unit = u
                        break
                concepts = [rag_matches[0].excerpt[:50]]
                source_refs.append(
                    SourceRef(
                        source_id=f"src_{rag_matches[0].chunk_id}",
                        document_id=rag_matches[0].document_id,
                        filename=rag_matches[0].document_id,
                        page=rag_matches[0].page,
                        chunk_id=rag_matches[0].chunk_id,
                    )
                )

            return SyllabusAssessment(
                query=query,
                is_in_syllabus=True,
                matched_unit=unit,
                matched_concepts=concepts,
                verdict="IN_SYLLABUS",
                response_text=f"The topic '{query}' is covered under Unit {unit} in your college syllabus.",
                is_external_knowledge=False,
                source_label="COLLEGE_COURSE_MATERIAL",
                source_refs=source_refs,
            )

        # If neither KB nor RAG finds grounding: out-of-syllabus
        return self._handle_out_of_syllabus(query, reason="Not found in syllabus", allow_general=allow_general_knowledge)

    def _handle_out_of_syllabus(
        self,
        query: str,
        reason: str,
        allow_general: bool,
    ) -> SyllabusAssessment:
        if not allow_general:
            return SyllabusAssessment(
                query=query,
                is_in_syllabus=False,
                matched_unit=None,
                matched_concepts=[],
                verdict="NOT_FOUND_IN_COURSE_MATERIAL",
                response_text=(
                    f"NOT FOUND IN COURSE MATERIAL: The topic '{query}' is not covered in your college "
                    f"Machine Learning (AD5305 / CS4403) syllabus (Units I–V). "
                    f"To study this, please enable 'General Knowledge Mode' explicitly."
                ),
                is_external_knowledge=False,
                source_label="COLLEGE_COURSE_BOUNDARY_CHECK",
                source_refs=[],
            )
        else:
            return SyllabusAssessment(
                query=query,
                is_in_syllabus=False,
                matched_unit=None,
                matched_concepts=[],
                verdict="NOT_FOUND_IN_COURSE_MATERIAL",
                response_text=(
                    f"[EXTERNAL_GENERAL_KNOWLEDGE (NOT IN COLLEGE SYLLABUS)] "
                    f"While '{query}' is outside your college AD5305 / CS4403 syllabus, here is the general overview: "
                    f"{query} is an advanced topic that extends beyond the prescribed Units I–V course notes."
                ),
                is_external_knowledge=True,
                source_label="EXTERNAL_GENERAL_KNOWLEDGE (NOT IN COLLEGE SYLLABUS)",
                source_refs=[],
            )

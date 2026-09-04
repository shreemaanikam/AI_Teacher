"""
RAG Adapter for Member 1 Integration.
Defines contracts and fallback retrieval for grounded educational source chunks.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceChunk(BaseModel):
    chunk_id: str
    document_id: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = None
    content: str
    relevance_score: float = 1.0


class EvidencePack(BaseModel):
    query: str
    concept: str
    chunks: List[EvidenceChunk] = Field(default_factory=list)
    is_grounded: bool = True
    grounding_notes: Optional[str] = None


from app.rag.retriever import HybridRetriever
from app.rag.models import GroundingLevel


class EducationalRAGAdapter:
    """Consumes Module 2 RAG retrieval engine to provide grounded educational evidence packs."""

    def __init__(self, retriever: Optional[HybridRetriever] = None):
        self.retriever = retriever or HybridRetriever()

    def retrieve_concept_evidence(self, concept: str, document_id: Optional[str] = None) -> EvidencePack:
        evidence_pkg = self.retriever.retrieve_evidence(
            query=f"Explain {concept} and formulas and definitions",
            target_concept=concept,
            document_id=document_id,
            top_k=3,
        )

        chunks = []
        for it in evidence_pkg.evidence_items:
            chunks.append(
                EvidenceChunk(
                    chunk_id=it.chunk_id,
                    document_id=it.document_id,
                    section=f"{it.chapter} - {it.section}" if it.chapter else it.section,
                    page=it.page,
                    content=it.excerpt,
                    relevance_score=it.relevance_score,
                )
            )

        is_grounded = evidence_pkg.grounding_level in [GroundingLevel.SUPPORTED, GroundingLevel.PARTIALLY_SUPPORTED]

        if not chunks:
            chunks.append(
                EvidenceChunk(
                    chunk_id="chk_gen",
                    content=f"Fundamental educational principles and definitions for {concept}.",
                    relevance_score=0.85,
                )
            )

        return EvidencePack(
            query=f"Explain {concept} and formulas",
            concept=concept,
            chunks=chunks,
            is_grounded=is_grounded,
            grounding_notes=evidence_pkg.limitations_or_gaps,
        )

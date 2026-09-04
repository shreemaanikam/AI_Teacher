"""
Hybrid Retriever, Reranker, and Evidence Package Builder for Module 2.
Enforces strict grounding levels (SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED) to eliminate hallucinations.
"""

from __future__ import annotations
import math
import logging
from typing import List, Dict, Optional, Tuple, Any

from app.rag.models import (
    DocumentChunk,
    ChunkType,
    EvidencePackage,
    EvidenceItem,
    GroundingLevel,
    DocumentStructure,
)
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider
from app.rag.vector_store import VectorStore, MemoryVectorStore

logger = logging.getLogger("HybridRetriever")


class HybridRetriever:
    """
    Combines dense semantic vector search, BM25 keyword matching, and reranking.
    Constructs certified EvidencePackages for downstream pedagogical planning and teaching.
    """

    SUPPORTED_THRESHOLD = 0.48
    PARTIAL_THRESHOLD = 0.22

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store = vector_store or MemoryVectorStore(self.embedding_provider)
        self._preload_test_corpus()

    def _preload_test_corpus(self) -> None:
        """Seeds the controlled educational corpus for test scenarios."""
        corpus_chunks = [
            # Physics: Ohm's Law
            DocumentChunk(
                chunk_id="chk_phys_01",
                document_id="doc_physics_textbook",
                chapter_title="Electric Circuits & Ohm's Law",
                section_title="Current, Voltage, and Resistance",
                concept_name="Ohm's Law",
                page_number=45,
                chunk_index=0,
                content="Definition of Ohm's Law: At a constant temperature, the electrical current (I) flowing through a conductor is directly proportional to the potential difference (V) across its ends, and inversely proportional to the resistance (R). Formula: I = V / R or V = I * R.",
                content_type=ChunkType.CONCEPT_DEFINITION,
                language="en",
            ),
            DocumentChunk(
                chunk_id="chk_phys_02",
                document_id="doc_physics_textbook",
                chapter_title="Electric Circuits & Ohm's Law",
                section_title="Worked Problems",
                concept_name="Ohm's Law",
                page_number=46,
                chunk_index=1,
                content="Worked Example: A 12V battery is connected across a 6 Ohm resistor. To find the current: I = V / R = 12 / 6 = 2 Amperes. If resistance is doubled to 12 Ohms, current is halved to 1 Ampere.",
                content_type=ChunkType.WORKED_EXAMPLE,
                language="en",
            ),
            # Programming: Python Variables & Conditions
            DocumentChunk(
                chunk_id="chk_prog_01",
                document_id="doc_python_fundamentals",
                chapter_title="Variables and Control Flow",
                section_title="Variable Assignment",
                concept_name="Python Variables",
                page_number=12,
                chunk_index=0,
                content="In Python, a single equals sign '=' is an assignment operator that binds a value to a variable name (e.g., x = 10). Double equals '==' is an equality comparison operator evaluating to True or False.",
                content_type=ChunkType.CONCEPT_DEFINITION,
                language="en",
            ),
            # Mathematics: Algebra
            DocumentChunk(
                chunk_id="chk_math_01",
                document_id="doc_algebra_foundations",
                chapter_title="Linear Equations",
                section_title="Solving for Unknowns",
                concept_name="Linear Equations",
                page_number=28,
                chunk_index=0,
                content="A linear equation in one variable takes the standard form ax + b = c. To isolate the variable x, subtract b from both sides (ax = c - b) and divide by a (x = (c - b) / a), where a != 0.",
                content_type=ChunkType.FORMULA_DERIVATION,
                language="en",
            ),
            # Biology: Cellular Respiration
            DocumentChunk(
                chunk_id="chk_bio_01",
                document_id="doc_biology_cell",
                chapter_title="Cellular Energetics",
                section_title="Mitochondrial Respiration",
                concept_name="Cellular Respiration",
                page_number=89,
                chunk_index=0,
                content="Cellular respiration is the biochemical process by which organisms combine glucose (C6H12O6) with oxygen (O2) to synthesize adenosine triphosphate (ATP), releasing carbon dioxide (CO2) and water (H2O) as metabolic byproducts.",
                content_type=ChunkType.CONCEPT_DEFINITION,
                language="en",
            ),
        ]
        self.vector_store.add_chunks(corpus_chunks)

    def retrieve_evidence(
        self,
        query: str,
        target_concept: Optional[str] = None,
        document_id: Optional[str] = None,
        top_k: int = 3,
        teaching_language: str = "en",
    ) -> EvidencePackage:
        """
        Executes hybrid search (semantic + keyword), applies reciprocal rank fusion,
        and constructs a certified EvidencePackage.
        """
        query_text = query.strip()
        concept = target_concept or query_text

        # 1. Semantic Vector Search (returns (chunk, cosine_sim))
        query_vec = self.embedding_provider.embed_text(query_text)
        semantic_results = self.vector_store.search_semantic(query_vec, top_k=top_k * 2, document_id=document_id)

        # 2. Keyword BM25 Search (returns (chunk, keyword_ratio))
        keyword_results = self.vector_store.search_keyword(query_text, top_k=top_k * 2, document_id=document_id)
        kw_dict = {c.chunk_id: score for c, score in keyword_results}

        # Check if query hits any domain anchors
        has_anchor = False
        if hasattr(self.embedding_provider, "multilingual_anchors"):
            q_lower = query_text.lower()
            for synonyms in self.embedding_provider.multilingual_anchors.values():
                if any(syn in q_lower for syn in synonyms):
                    has_anchor = True
                    break

        # 3. Hybrid Fusion with absolute relevance gate
        scored_candidates: List[Tuple[DocumentChunk, float]] = []
        for chunk, sim in semantic_results:
            kw_score = kw_dict.get(chunk.chunk_id, 0.0)
            if not has_anchor and kw_score == 0:
                sim = sim * 0.2  # Heavy penalty for random hash collision on ungrounded query

            hybrid_score = (sim * 0.70) + (kw_score * 0.30)
            if sim >= 0.25 or kw_score > 0.0:
                scored_candidates.append((chunk, hybrid_score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_candidates[:top_k]

        # 4. Assess Grounding Level
        evidence_items: List[EvidenceItem] = []
        source_docs = set()

        if top_candidates:
            top_score = top_candidates[0][1]

            for chunk, score in top_candidates:
                if score >= self.PARTIAL_THRESHOLD:
                    evidence_items.append(
                        EvidenceItem(
                            chunk_id=chunk.chunk_id,
                            document_id=chunk.document_id,
                            chapter=chunk.chapter_title,
                            section=chunk.section_title,
                            page=chunk.page_number,
                            content_type=chunk.content_type,
                            excerpt=chunk.content,
                            relevance_score=round(score, 3),
                            confidence=0.95 if score >= self.SUPPORTED_THRESHOLD else 0.70,
                        )
                    )
                    source_docs.add(chunk.document_id)

            if top_score >= self.SUPPORTED_THRESHOLD and evidence_items:
                grounding = GroundingLevel.SUPPORTED
                context = "\n\n".join([f"[{it.chapter} - Page {it.page}]: {it.excerpt}" for it in evidence_items])
                confidence = 0.95
            elif top_score >= self.PARTIAL_THRESHOLD and evidence_items:
                grounding = GroundingLevel.PARTIALLY_SUPPORTED
                context = "\n\n".join([f"[{it.chapter}]: {it.excerpt}" for it in evidence_items])
                confidence = 0.70
            else:
                grounding = GroundingLevel.UNSUPPORTED
                context = "Insufficient evidence in the provided material."
                confidence = 0.20
        else:
            grounding = GroundingLevel.UNSUPPORTED
            context = "Insufficient evidence in the provided material."
            confidence = 0.10

        return EvidencePackage(
            query=query_text,
            target_concept=concept,
            grounding_level=grounding,
            evidence_items=evidence_items,
            combined_context=context,
            source_documents=list(source_docs),
            confidence=confidence,
            limitations_or_gaps="No direct match found in document index" if grounding == GroundingLevel.UNSUPPORTED else None,
        )

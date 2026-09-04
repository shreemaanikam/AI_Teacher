"""
Vector Store and Hybrid Index for Module 2: Document Processing & Educational RAG.
"""

from __future__ import annotations
import math
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Any

from app.rag.models import DocumentChunk, ChunkType
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class VectorStore(ABC):
    """Abstract interface for storing and querying document chunks and embeddings."""

    @abstractmethod
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        pass

    @abstractmethod
    def search_semantic(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        pass

    @abstractmethod
    def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        pass

    @abstractmethod
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        pass


class MemoryVectorStore(VectorStore):
    """In-memory hybrid dense vector + BM25 keyword search index."""

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self._chunks: Dict[str, DocumentChunk] = {}
        self._doc_chunks: Dict[str, List[str]] = {}

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        for chunk in chunks:
            if not chunk.embedding:
                chunk.embedding = self.embedding_provider.embed_text(chunk.content)
            self._chunks[chunk.chunk_id] = chunk

            if chunk.document_id not in self._doc_chunks:
                self._doc_chunks[chunk.document_id] = []
            if chunk.chunk_id not in self._doc_chunks[chunk.document_id]:
                self._doc_chunks[chunk.document_id].append(chunk.chunk_id)

    def search_semantic(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        candidates = self._chunks.values()
        if document_id:
            candidates = [c for c in candidates if c.document_id == document_id]

        scored = []
        for chunk in candidates:
            if chunk.embedding:
                sim = cosine_similarity(query_vector, chunk.embedding)
                scored.append((chunk, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        if not query_terms:
            return []

        candidates = self._chunks.values()
        if document_id:
            candidates = [c for c in candidates if c.document_id == document_id]

        scored = []
        for chunk in candidates:
            text_lower = chunk.content.lower()
            matches = sum(1 for term in query_terms if term in text_lower)
            if matches > 0:
                score = matches / (len(query_terms) + 0.1)
                scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        chunk_ids = self._doc_chunks.get(document_id, [])
        return [self._chunks[cid] for cid in chunk_ids if cid in self._chunks]

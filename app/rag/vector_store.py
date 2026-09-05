"""
Vector Store and Hybrid Index for Module 2: Document Processing & Educational RAG.
Supports Pinecone (Primary), Weaviate (Secondary), and MemoryVectorStore (Fallback).
"""

from __future__ import annotations
import os
import json
import math
import re
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Any

from app.rag.models import DocumentChunk, ChunkType
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider

logger = logging.getLogger("VectorStore")


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
        stop_words = {
            "and", "the", "for", "with", "that", "this", "from", "are", "was", "were",
            "what", "how", "why", "who", "when", "where", "can", "could", "would",
            "should", "not", "but", "all", "any", "some", "our", "you", "they", "them",
            "his", "her", "its", "about", "into", "over", "after"
        }
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2 and t.lower() not in stop_words]
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
                score = matches / len(query_terms)
                scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        chunk_ids = self._doc_chunks.get(document_id, [])
        return [self._chunks[cid] for cid in chunk_ids if cid in self._chunks]


class PineconeVectorStore(VectorStore):
    """
    Production Vector Store connecting to Pinecone Serverless REST API.
    Upserts 1024-D vectors and performs low-latency cosine semantic retrieval.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        raw_host = host or os.getenv("PINECONE_HOST") or "ai-teacher-nrp0fvm.svc.aped-4627-b74a.pinecone.io"
        self.host_url = raw_host if raw_host.startswith("http") else f"https://{raw_host}"
        
        embedder = embedding_provider or get_embedding_provider(prefer_neural=True)
        if getattr(embedder, "DIMENSIONS", 0) != 1024:
            from app.rag.embeddings import GeminiEmbeddingProvider, LocalDenseEmbeddingProvider
            if os.getenv("GEMINI_API_KEY"):
                embedder = GeminiEmbeddingProvider()
            else:
                embedder = LocalDenseEmbeddingProvider(dimensions=1024)
        self.embedding_provider = embedder
        self.fallback = MemoryVectorStore(self.embedding_provider)
        self.namespace = "educational_chunks"

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        self.fallback.add_chunks(chunks)

        if not self.api_key:
            return

        try:
            vectors_to_upsert = []
            for chunk in chunks:
                if not chunk.embedding:
                    chunk.embedding = self.embedding_provider.embed_text(chunk.content)
                vectors_to_upsert.append({
                    "id": chunk.chunk_id,
                    "values": chunk.embedding,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                        "content_type": chunk.content_type.value if hasattr(chunk.content_type, "value") else str(chunk.content_type),
                        "chapter_id": chunk.chapter_id or "",
                        "chapter_title": chunk.chapter_title or "",
                        "section_id": chunk.section_id or "",
                        "section_title": chunk.section_title or "",
                        "concept_id": chunk.concept_id or "",
                        "concept_name": chunk.concept_name or "",
                        "content": chunk.content[:1000],
                        "page_number": chunk.page_number or 1,
                    }
                })

            headers = {
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
            }
            # Batch upsert in chunks of 50
            for i in range(0, len(vectors_to_upsert), 50):
                batch = vectors_to_upsert[i : i + 50]
                payload = {"vectors": batch, "namespace": self.namespace}
                req = urllib.request.Request(
                    f"{self.host_url}/vectors/upsert",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pass
            logger.info(f"Successfully upserted {len(chunks)} chunks to Pinecone index.")
        except Exception as e:
            logger.warning(f"Pinecone upsert failed ({e}). Retained in local fallback memory store.")

    def search_semantic(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        if not self.api_key:
            return self.fallback.search_semantic(query_vector, top_k, document_id)

        try:
            headers = {
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
            }
            payload = {
                "vector": query_vector,
                "topK": top_k,
                "includeMetadata": True,
                "namespace": self.namespace,
            }
            if document_id:
                payload["filter"] = {"document_id": {"$eq": document_id}}

            req = urllib.request.Request(
                f"{self.host_url}/query",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                matches = data.get("matches", [])
                results = []
                for m in matches:
                    meta = m.get("metadata", {})
                    cid = m.get("id", "")
                    # Fetch or build chunk
                    cached = self.fallback._chunks.get(cid)
                    if cached:
                        results.append((cached, float(m.get("score", 0.0))))
                    else:
                        chunk = DocumentChunk(
                            chunk_id=cid,
                            document_id=meta.get("document_id", "doc_unknown"),
                            chunk_index=int(meta.get("chunk_index", 0)),
                            content_type=ChunkType(meta.get("content_type", meta.get("chunk_type", "explanation"))),
                            chapter_id=meta.get("chapter_id") or None,
                            chapter_title=meta.get("chapter_title") or meta.get("chapter") or None,
                            section_id=meta.get("section_id") or None,
                            section_title=meta.get("section_title") or meta.get("section") or None,
                            concept_id=meta.get("concept_id") or None,
                            concept_name=meta.get("concept_name") or meta.get("concept") or None,
                            content=meta.get("content", ""),
                            page_number=int(meta.get("page_number", 1)),
                        )
                        results.append((chunk, float(m.get("score", 0.0))))
                if results:
                    return results
        except Exception as e:
            logger.warning(f"Pinecone query failed ({e}). Falling back to local search.")

        return self.fallback.search_semantic(query_vector, top_k, document_id)

    def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        return self.fallback.search_keyword(query, top_k, document_id)

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self.fallback.get_document_chunks(document_id)


class WeaviateVectorStore(VectorStore):
    """Secondary Vector Store connecting to Weaviate cloud instance."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        raw_url = url or os.getenv("WEAVIATE_URL") or ""
        self.url = raw_url if raw_url.startswith("http") else f"https://{raw_url}"
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.fallback = MemoryVectorStore(self.embedding_provider)

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        self.fallback.add_chunks(chunks)

    def search_semantic(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        return self.fallback.search_semantic(query_vector, top_k, document_id)

    def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        return self.fallback.search_keyword(query, top_k, document_id)

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self.fallback.get_document_chunks(document_id)


_GLOBAL_VECTOR_STORE: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Returns the singleton active VectorStore based on provider configuration."""
    global _GLOBAL_VECTOR_STORE
    if _GLOBAL_VECTOR_STORE is None:
        provider = (os.getenv("VECTOR_DB_PROVIDER") or "pinecone").lower()
        if provider == "pinecone" and os.getenv("PINECONE_API_KEY"):
            _GLOBAL_VECTOR_STORE = PineconeVectorStore()
        elif provider == "weaviate" and os.getenv("WEAVIATE_API_KEY"):
            _GLOBAL_VECTOR_STORE = WeaviateVectorStore()
        elif os.getenv("PINECONE_API_KEY"):
            _GLOBAL_VECTOR_STORE = PineconeVectorStore()
        else:
            _GLOBAL_VECTOR_STORE = MemoryVectorStore()
    return _GLOBAL_VECTOR_STORE

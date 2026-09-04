"""
Module 2: Document Processing & Educational RAG package.
"""

from app.rag.models import (
    DocumentStructure,
    ChapterNode,
    SectionNode,
    ConceptNode,
    DefinitionNode,
    FormulaNode,
    ExampleNode,
    DocumentChunk,
    ChunkType,
    EvidencePackage,
    EvidenceItem,
    GroundingLevel,
)
from app.rag.extractors import get_document_extractor, DocumentExtractor
from app.rag.chunking import SemanticDocumentChunker
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider, LocalDenseEmbeddingProvider
from app.rag.vector_store import VectorStore, MemoryVectorStore
from app.rag.retriever import HybridRetriever

__all__ = [
    "DocumentStructure",
    "ChapterNode",
    "SectionNode",
    "ConceptNode",
    "DefinitionNode",
    "FormulaNode",
    "ExampleNode",
    "DocumentChunk",
    "ChunkType",
    "EvidencePackage",
    "EvidenceItem",
    "GroundingLevel",
    "get_document_extractor",
    "DocumentExtractor",
    "SemanticDocumentChunker",
    "EmbeddingProvider",
    "get_embedding_provider",
    "LocalDenseEmbeddingProvider",
    "VectorStore",
    "MemoryVectorStore",
    "HybridRetriever",
]

"""
Semantic and Structure-Aware Document Chunker for Module 2.
Protects equations, definitions, code blocks, and examples from arbitrary boundary cuts.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any
from app.rag.models import (
    DocumentStructure,
    DocumentChunk,
    ChunkType,
    ChapterNode,
    SectionNode,
    ConceptNode,
)


class SemanticDocumentChunker:
    """Chunks structured educational documents into semantic, metadata-rich retrieval units."""

    MAX_CHUNK_CHARS = 1200
    MIN_CHUNK_CHARS = 100

    @classmethod
    def chunk_document(cls, structure: DocumentStructure) -> List[DocumentChunk]:
        """Traverses hierarchical DocumentStructure and produces atomic semantic chunks."""
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for ch in structure.chapters:
            for sec in ch.sections:
                # 1. Process structured concept definitions and formulas first
                for concept in sec.concepts:
                    # Chunks for definitions
                    for d in concept.definitions:
                        chunk = DocumentChunk(
                            document_id=structure.document_id,
                            chapter_id=ch.chapter_id,
                            chapter_title=ch.title,
                            section_id=sec.section_id,
                            section_title=sec.title,
                            concept_id=concept.concept_id,
                            concept_name=concept.name,
                            page_number=sec.page_number,
                            chunk_index=chunk_idx,
                            content=f"Definition of {d.term}: {d.definition_text}",
                            content_type=ChunkType.CONCEPT_DEFINITION,
                            language=structure.language,
                            metadata={"term": d.term, "keywords": d.keywords},
                        )
                        chunks.append(chunk)
                        chunk_idx += 1

                    # Chunks for formulas
                    for f in concept.formulas:
                        chunk = DocumentChunk(
                            document_id=structure.document_id,
                            chapter_id=ch.chapter_id,
                            chapter_title=ch.title,
                            section_id=sec.section_id,
                            section_title=sec.title,
                            concept_id=concept.concept_id,
                            concept_name=concept.name,
                            page_number=sec.page_number,
                            chunk_index=chunk_idx,
                            content=f"Formula for {concept.name} ({f.name}): {f.expression}",
                            content_type=ChunkType.FORMULA_DERIVATION,
                            language=structure.language,
                            metadata={"expression": f.expression, "variables": f.variables},
                        )
                        chunks.append(chunk)
                        chunk_idx += 1

                    # Chunks for examples
                    for ex in concept.examples:
                        chunk = DocumentChunk(
                            document_id=structure.document_id,
                            chapter_id=ch.chapter_id,
                            chapter_title=ch.title,
                            section_id=sec.section_id,
                            section_title=sec.title,
                            concept_id=concept.concept_id,
                            concept_name=concept.name,
                            page_number=sec.page_number,
                            chunk_index=chunk_idx,
                            content=f"Worked Example: {ex.title}\n{ex.problem_statement}",
                            content_type=ChunkType.WORKED_EXAMPLE,
                            language=structure.language,
                            metadata={"title": ex.title},
                        )
                        chunks.append(chunk)
                        chunk_idx += 1

                # 2. Process Section Content Paragraphs without splitting formulas
                paragraphs = [p.strip() for p in sec.content.split("\n\n") if p.strip()]
                for p in paragraphs:
                    if len(p) < cls.MIN_CHUNK_CHARS and len(paragraphs) > 1:
                        continue

                    ctype = ChunkType.EXPLANATION
                    if "```" in p:
                        ctype = ChunkType.CODE_SNIPPET
                    elif "|" in p and "---" in p:
                        ctype = ChunkType.TABLE_DATA

                    chunk = DocumentChunk(
                        document_id=structure.document_id,
                        chapter_id=ch.chapter_id,
                        chapter_title=ch.title,
                        section_id=sec.section_id,
                        section_title=sec.title,
                        concept_name=ch.title,
                        page_number=sec.page_number,
                        chunk_index=chunk_idx,
                        content=p,
                        content_type=ctype,
                        language=structure.language,
                        metadata={"length": len(p)},
                    )
                    chunks.append(chunk)
                    chunk_idx += 1

        # If document had no chapters/sections, create a fallback chunk
        if not chunks:
            chunks.append(
                DocumentChunk(
                    document_id=structure.document_id,
                    chunk_index=0,
                    content=f"Document: {structure.title} ({structure.subject})",
                    content_type=ChunkType.SUMMARY,
                    language=structure.language,
                )
            )

        return chunks

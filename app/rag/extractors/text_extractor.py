"""
Text and Markdown Document Extractor for Module 2.
Parses structural hierarchy (Chapters, Sections, Definitions, Formulas, Examples) from plaintext or Markdown.
"""

from __future__ import annotations
import re
import os
from typing import List, Dict, Optional
from app.rag.extractors.base import DocumentExtractor
from app.rag.models import (
    DocumentStructure,
    ChapterNode,
    SectionNode,
    ConceptNode,
    DefinitionNode,
    FormulaNode,
    ExampleNode,
)


class TextDocumentExtractor(DocumentExtractor):
    """Extracts structured educational hierarchy from Markdown or TXT documents."""

    def extract_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        subject: str = "physics",
        language: str = "en",
    ) -> DocumentStructure:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        lines = raw_text.splitlines()
        doc_title = os.path.splitext(filename)[0].replace("_", " ").title()

        chapters: List[ChapterNode] = []
        current_chapter: Optional[ChapterNode] = None
        current_section: Optional[SectionNode] = None
        current_concept: Optional[ConceptNode] = None

        # Fallback chapter if no headers
        current_chapter = ChapterNode(
            number="1",
            title=doc_title,
            sections=[],
        )
        current_section = SectionNode(
            title="Overview",
            page_number=1,
            content="",
            concepts=[],
        )
        current_chapter.sections.append(current_section)
        chapters.append(current_chapter)

        accumulated_lines: List[str] = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if line is Chapter header (# Chapter 1 ... or # Topic)
            if trimmed.startswith("# ") or re.match(r"^Chapter\s+[0-9IVX]+", trimmed, re.IGNORECASE):
                ch_title = re.sub(r"^#+\s*", "", trimmed).strip()
                current_chapter = ChapterNode(
                    number=str(len(chapters) + 1),
                    title=ch_title,
                    sections=[],
                )
                chapters.append(current_chapter)
                current_section = SectionNode(
                    title="Introduction",
                    page_number=1,
                    content="",
                    concepts=[],
                )
                current_chapter.sections.append(current_section)
                continue

            # Check if line is Section header (## ...)
            if trimmed.startswith("## ") or re.match(r"^Section\s+[0-9.]+", trimmed, re.IGNORECASE):
                sec_title = re.sub(r"^#+\s*", "", trimmed).strip()
                current_section = SectionNode(
                    title=sec_title,
                    page_number=1,
                    content="",
                    concepts=[],
                )
                current_chapter.sections.append(current_section)
                continue

            # Check if line is Concept header (### ...)
            if trimmed.startswith("### "):
                concept_name = trimmed.replace("### ", "").strip()
                current_concept = ConceptNode(
                    name=concept_name,
                    summary=concept_name,
                    definitions=[],
                    formulas=[],
                    examples=[],
                    key_terms=[],
                )
                current_section.concepts.append(current_concept)
                continue

            # Detect formulas e.g. V = I * R or $$...$$
            if re.search(r"\b[A-Za-z]\s*=\s*[A-Za-z0-9\s*+\-/^().]+", trimmed) and any(op in trimmed for op in ["=", "*", "/", "+", "-"]):
                if current_concept:
                    current_concept.formulas.append(
                        FormulaNode(name="Governing Equation", expression=trimmed)
                    )

            # Detect definitions e.g. Definition: ... or "is defined as"
            if "definition:" in trimmed.lower() or "is defined as" in trimmed.lower() or "states that" in trimmed.lower():
                if current_concept:
                    current_concept.definitions.append(
                        DefinitionNode(term=current_concept.name, definition_text=trimmed)
                    )

            # Detect examples e.g. Example: ...
            if trimmed.lower().startswith("example") or "worked example:" in trimmed.lower():
                if current_concept:
                    current_concept.examples.append(
                        ExampleNode(title="Worked Example", problem_statement=trimmed)
                    )

            accumulated_lines.append(trimmed)
            if current_section:
                current_section.content += trimmed + "\n"

        return DocumentStructure(
            document_id=document_id,
            title=doc_title,
            subject=subject,
            total_pages=max(1, len(accumulated_lines) // 40),
            language=language,
            chapters=chapters,
        )

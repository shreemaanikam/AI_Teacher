"""
PDF Document Extractor for Module 2.
Utilizes PyMuPDF (fitz) when installed, or native PDF object stream parsing as zero-dependency fallback.
"""

from __future__ import annotations
import re
import os
from typing import List, Optional
from app.rag.extractors.base import DocumentExtractor
from app.rag.extractors.text_extractor import TextDocumentExtractor
from app.rag.models import (
    DocumentStructure,
    ChapterNode,
    SectionNode,
    ConceptNode,
    DefinitionNode,
    FormulaNode,
    ExampleNode,
)


class PDFDocumentExtractor(DocumentExtractor):
    """Extracts pages, chapters, and concepts from PDF files."""

    def __init__(self):
        self._text_extractor = TextDocumentExtractor()

    def _extract_with_fitz(self, file_path: str) -> List[str]:
        import fitz  # type: ignore
        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        return pages_text

    def _extract_native_pdf_text(self, file_path: str) -> List[str]:
        """Extracts text chunks from PDF streams without external dependencies."""
        with open(file_path, "rb") as f:
            content = f.read()

        # Extract text within BT ... ET blocks or parentheses in Tj / TJ operators
        text_parts = []
        stream_matches = re.findall(rb"\((.*?)\)\s*Tj", content)
        for sm in stream_matches:
            try:
                decoded = sm.decode("utf-8", errors="ignore")
                if len(decoded.strip()) > 1:
                    text_parts.append(decoded)
            except Exception:
                continue

        if not text_parts:
            # Fallback: extract printable ASCII / UTF-8 character sequences
            printable = re.findall(rb"[a-zA-Z0-9.,;:!?'\"\s\-\(\)\+\=\/\$\%\#]{4,}", content)
            text_parts = [p.decode("utf-8", errors="ignore") for p in printable if len(p.strip()) > 10]

        return ["\n".join(text_parts)]

    def extract_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        subject: str = "physics",
        language: str = "en",
    ) -> DocumentStructure:
        pages_text = []
        try:
            pages_text = self._extract_with_fitz(file_path)
        except Exception:
            pages_text = self._extract_native_pdf_text(file_path)

        full_text = "\n\n".join(pages_text)
        if not full_text.strip():
            full_text = f"# {filename}\n## Overview\nGeneral educational document on {subject}."

        # Pass extracted text to structural parser
        # Temporary text file simulation
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(full_text)
            tmp_path = tmp.name

        try:
            structure = self._text_extractor.extract_document(
                file_path=tmp_path,
                document_id=document_id,
                filename=filename,
                subject=subject,
                language=language,
            )
            structure.total_pages = max(1, len(pages_text))
            return structure
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

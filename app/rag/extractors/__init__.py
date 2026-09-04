"""
Extractors factory for Module 2: Document Processing & Educational RAG.
"""

from __future__ import annotations
import os
from app.rag.extractors.base import DocumentExtractor
from app.rag.extractors.pdf_extractor import PDFDocumentExtractor
from app.rag.extractors.docx_extractor import DocxDocumentExtractor
from app.rag.extractors.pptx_extractor import PptxDocumentExtractor
from app.rag.extractors.text_extractor import TextDocumentExtractor
from app.rag.extractors.ocr_extractor import OCRDocumentExtractor


def get_document_extractor(file_path: str) -> DocumentExtractor:
    """Returns the specialized DocumentExtractor based on file extension."""
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".pdf":
        return PDFDocumentExtractor()
    elif ext in {".docx", ".doc"}:
        return DocxDocumentExtractor()
    elif ext in {".pptx", ".ppt"}:
        return PptxDocumentExtractor()
    return TextDocumentExtractor()


__all__ = [
    "DocumentExtractor",
    "PDFDocumentExtractor",
    "DocxDocumentExtractor",
    "PptxDocumentExtractor",
    "TextDocumentExtractor",
    "OCRDocumentExtractor",
    "get_document_extractor",
]

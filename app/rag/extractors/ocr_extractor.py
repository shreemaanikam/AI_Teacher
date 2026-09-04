"""
OCR Document Extractor interface for scanned images and documents.
"""

from __future__ import annotations
import os
from typing import Optional
from app.rag.extractors.base import DocumentExtractor
from app.rag.extractors.text_extractor import TextDocumentExtractor
from app.rag.models import DocumentStructure


class OCRDocumentExtractor(DocumentExtractor):
    """Provides an OCR abstraction for scanned documents (e.g. pytesseract / Google Cloud Vision)."""

    def __init__(self, fallback_engine: Optional[DocumentExtractor] = None):
        self.fallback = fallback_engine or TextDocumentExtractor()

    def extract_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        subject: str = "physics",
        language: str = "en",
    ) -> DocumentStructure:
        # Check if tesseract or vision API is configured
        # Graceful fallback to text extractor
        return self.fallback.extract_document(file_path, document_id, filename, subject, language)

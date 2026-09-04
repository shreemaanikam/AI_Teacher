"""
Base document extractor interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.rag.models import DocumentStructure


class DocumentExtractor(ABC):
    """Abstract interface for extracting text, chapters, sections, and metadata from educational files."""

    @abstractmethod
    def extract_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        subject: str = "physics",
        language: str = "en",
    ) -> DocumentStructure:
        """Parses the document into a hierarchical DocumentStructure."""
        pass

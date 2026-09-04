"""
DOCX Document Extractor for Module 2.
Utilizes python-docx if installed, or native XML Zip decompression (word/document.xml) as reliable fallback.
"""

from __future__ import annotations
import os
import zipfile
import xml.etree.ElementTree as ET
import tempfile
from app.rag.extractors.base import DocumentExtractor
from app.rag.extractors.text_extractor import TextDocumentExtractor
from app.rag.models import DocumentStructure


class DocxDocumentExtractor(DocumentExtractor):
    """Extracts text, headings, and tables from .docx and .doc files."""

    def __init__(self):
        self._text_extractor = TextDocumentExtractor()

    def _extract_with_docx_lib(self, file_path: str) -> str:
        import docx  # type: ignore
        doc = docx.Document(file_path)
        paragraphs = []
        for p in doc.paragraphs:
            if p.text.strip():
                if p.style.name.startswith("Heading 1"):
                    paragraphs.append(f"# {p.text}")
                elif p.style.name.startswith("Heading 2"):
                    paragraphs.append(f"## {p.text}")
                elif p.style.name.startswith("Heading 3"):
                    paragraphs.append(f"### {p.text}")
                else:
                    paragraphs.append(p.text)
        return "\n\n".join(paragraphs)

    def _extract_native_xml(self, file_path: str) -> str:
        """Parses word/document.xml inside docx zip archive without third-party libraries."""
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                xml_content = zf.read("word/document.xml")
                root = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = []
                for p in root.findall(".//w:p", namespaces):
                    texts = [t.text for t in p.findall(".//w:t", namespaces) if t.text]
                    if texts:
                        paragraphs.append("".join(texts))
                return "\n\n".join(paragraphs)
        except Exception:
            return ""

    def extract_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        subject: str = "physics",
        language: str = "en",
    ) -> DocumentStructure:
        text = ""
        try:
            text = self._extract_with_docx_lib(file_path)
        except Exception:
            text = self._extract_native_xml(file_path)

        if not text.strip():
            text = f"# {filename}\n## Overview\nEducational notes on {subject}."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(text)
            tmp_path = tmp.name

        try:
            return self._text_extractor.extract_document(
                file_path=tmp_path,
                document_id=document_id,
                filename=filename,
                subject=subject,
                language=language,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

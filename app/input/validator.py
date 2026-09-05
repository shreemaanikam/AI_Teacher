"""
Security, MIME, and File Validation for Module 1: Student & Input Intelligence.
Guards against path traversal, oversized files, malicious filenames, and corrupted uploads.
"""

from __future__ import annotations
import os
import re
import hashlib
import uuid
from typing import Tuple, Optional, Set
from pydantic import BaseModel

ALLOWED_EXTENSIONS: Set[str] = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".md", ".markdown",
    ".png", ".jpg", ".jpeg"
}

ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/markdown",
    "image/png",
    "image/jpeg",
    "application/octet-stream",  # Often sent by browsers for binary formats
}

# Maximum file size allowed: 50MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


class FileValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    sanitized_filename: Optional[str] = None
    storage_filename: Optional[str] = None
    extension: Optional[str] = None
    file_size_bytes: int = 0
    sha256_checksum: Optional[str] = None


class InputSecurityValidator:
    """Validates uploaded files and raw user text inputs against security vulnerabilities."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Removes path traversal characters and unsafe symbols from client filename."""
        base = os.path.basename(filename)
        # Strip all directory traversal markers
        base = base.replace("..", "").replace("/", "").replace("\\", "")
        # Remove dangerous or non-printable characters
        sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
        return sanitized if sanitized else f"upload_{uuid.uuid4().hex[:8]}.txt"

    @classmethod
    def validate_file_bytes(
        cls,
        filename: str,
        content_bytes: bytes,
        declared_mime: Optional[str] = None,
    ) -> FileValidationResult:
        """
        Validates uploaded file bytes for size, extension, magic headers, and calculates checksum.
        """
        if not content_bytes or len(content_bytes) == 0:
            return FileValidationResult(is_valid=False, error_message="Uploaded file is completely empty (0 bytes).")

        file_size = len(content_bytes)
        if file_size > MAX_FILE_SIZE_BYTES:
            return FileValidationResult(
                is_valid=False,
                error_message=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB (Got {file_size / (1024 * 1024):.1f}MB).",
                file_size_bytes=file_size,
            )

        sanitized_name = cls.sanitize_filename(filename)
        _, ext = os.path.splitext(sanitized_name.lower())

        if ext not in ALLOWED_EXTENSIONS:
            return FileValidationResult(
                is_valid=False,
                error_message=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                sanitized_filename=sanitized_name,
                file_size_bytes=file_size,
            )

        # Magic bytes check
        if ext == ".pdf" and not content_bytes.startswith(b"%PDF"):
            return FileValidationResult(
                is_valid=False,
                error_message="Corrupted or invalid PDF file header (missing '%PDF' magic header).",
                sanitized_filename=sanitized_name,
                file_size_bytes=file_size,
            )

        if ext in {".docx", ".pptx"} and not content_bytes.startswith(b"PK\x03\x04"):
            return FileValidationResult(
                is_valid=False,
                error_message=f"Corrupted or invalid Office OpenXML file (missing ZIP header 'PK' for {ext}).",
                sanitized_filename=sanitized_name,
                file_size_bytes=file_size,
            )

        # Checksum calculation
        checksum = hashlib.sha256(content_bytes).hexdigest()
        storage_filename = f"{checksum[:16]}_{sanitized_name}"

        return FileValidationResult(
            is_valid=True,
            sanitized_filename=sanitized_name,
            storage_filename=storage_filename,
            extension=ext,
            file_size_bytes=file_size,
            sha256_checksum=checksum,
        )

    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 500) -> str:
        """Sanitizes user-provided topic or objective strings."""
        if not text:
            return ""
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        return cleaned.strip()[:max_length]

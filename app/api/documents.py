"""
Document management REST API endpoints for Module 2.
"""

from __future__ import annotations
import os
import uuid
from typing import Dict
from flask import Blueprint, request, jsonify

from app.input.validator import InputSecurityValidator
from app.rag.extractors import get_document_extractor
from app.rag.chunking import SemanticDocumentChunker
from app.rag.models import DocumentStructure
from app.rag.retriever import HybridRetriever

documents_blueprint = Blueprint("documents_api", __name__)

_GLOBAL_RETRIEVER = HybridRetriever()
_STRUCTURES_STORE: Dict[str, DocumentStructure] = {}

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@documents_blueprint.route("/documents/upload", methods=["POST"])
def upload_and_ingest():
    """Uploads and stores an educational document."""
    if "file" not in request.files:
        return jsonify({"error": "No 'file' provided in request."}), 400

    f = request.files["file"]
    raw_bytes = f.read()
    val = InputSecurityValidator.validate_file_bytes(f.filename, raw_bytes, f.mimetype)
    if not val.is_valid:
        return jsonify({"error": val.error_message}), 400

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    storage_path = os.path.join(UPLOAD_DIR, val.storage_filename)
    with open(storage_path, "wb") as out:
        out.write(raw_bytes)

    return jsonify({
        "success": True,
        "document_id": doc_id,
        "filename": val.sanitized_filename,
        "file_path": storage_path,
        "size_bytes": val.file_size_bytes,
    }), 201


@documents_blueprint.route("/documents/process", methods=["POST"])
def process_document():
    """Extracts hierarchy, chunks, and indexes a stored document into the vector store."""
    data = request.get_json(silent=True) or {}
    file_path = data.get("file_path")
    doc_id = data.get("document_id") or f"doc_{uuid.uuid4().hex[:8]}"
    filename = data.get("filename") or os.path.basename(file_path or "doc.txt")
    subject = data.get("subject", "physics")
    language = data.get("language", "en")

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"File not found at path: '{file_path}'"}), 400

    extractor = get_document_extractor(file_path)
    structure = extractor.extract_document(
        file_path=file_path,
        document_id=doc_id,
        filename=filename,
        subject=subject,
        language=language,
    )
    _STRUCTURES_STORE[doc_id] = structure

    # Semantic chunking and vector indexing
    chunks = SemanticDocumentChunker.chunk_document(structure)
    _GLOBAL_RETRIEVER.vector_store.add_chunks(chunks)

    return jsonify({
        "success": True,
        "document_id": doc_id,
        "title": structure.title,
        "subject": structure.subject,
        "total_chapters": len(structure.chapters),
        "total_chunks_indexed": len(chunks),
    })


@documents_blueprint.route("/documents/<document_id>", methods=["GET"])
def get_document_info(document_id: str):
    """Retrieves metadata for a processed document."""
    structure = _STRUCTURES_STORE.get(document_id)
    if not structure:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404
    return jsonify({
        "document_id": structure.document_id,
        "title": structure.title,
        "subject": structure.subject,
        "total_pages": structure.total_pages,
        "language": structure.language,
        "total_chapters": len(structure.chapters),
    })


@documents_blueprint.route("/documents/<document_id>/structure", methods=["GET"])
def get_document_structure(document_id: str):
    """Retrieves full chapter/section/concept hierarchy for a document."""
    structure = _STRUCTURES_STORE.get(document_id)
    if not structure:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404
    return jsonify({"success": True, "structure": structure.model_dump()})

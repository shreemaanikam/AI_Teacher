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
from app.rag.content_understanding import ContentUnderstandingService, CourseUnderstanding
from app.rag.knowledge_graph import KnowledgeGraphBuilder, EducationalKnowledgeGraph
from app.rag.upload_service import StudentUploadPipeline
from app.db.repository import get_teaching_repository
from app.auth.token_manager import extract_token_from_request, get_session_token_manager

documents_blueprint = Blueprint("documents_api", __name__)

_GLOBAL_RETRIEVER = HybridRetriever()
_STRUCTURES_STORE: Dict[str, DocumentStructure] = {}
_UNDERSTANDINGS_STORE: Dict[str, CourseUnderstanding] = {}
_UNDERSTANDING_SERVICE = ContentUnderstandingService()
_UPLOAD_PIPELINE = StudentUploadPipeline(retriever=_GLOBAL_RETRIEVER, understanding_service=_UNDERSTANDING_SERVICE)

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@documents_blueprint.route("/documents/upload", methods=["POST"])
def upload_and_ingest():
    """Uploads and stores an educational document, optionally executing full multi-stage pipeline."""
    if "file" not in request.files:
        return jsonify({"error": "No 'file' provided in request."}), 400

    f = request.files["file"]
    raw_bytes = f.read()
    auto_process = request.args.get("auto_process", "false").lower() in ("true", "1") or \
                   request.form.get("auto_process", "false").lower() in ("true", "1") or \
                   request.form.get("pipeline", "false").lower() in ("true", "1")
    student_id = request.form.get("student_id") or request.args.get("student_id") or "default_student"
    subject_hint = request.form.get("subject") or request.args.get("subject")
    course = request.form.get("course") or request.args.get("course")

    if auto_process:
        try:
            result = _UPLOAD_PIPELINE.process_file_upload(
                raw_bytes=raw_bytes,
                original_filename=f.filename,
                mimetype=f.mimetype or "application/octet-stream",
                student_id=student_id,
                subject_hint=subject_hint,
                course=course,
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Upload processing failed: {str(e)}"}), 500

    val = InputSecurityValidator.validate_file_bytes(f.filename, raw_bytes, f.mimetype)
    if not val.is_valid:
        return jsonify({"error": val.error_message}), 400

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    storage_path = os.path.join(UPLOAD_DIR, val.storage_filename)
    with open(storage_path, "wb") as out:
        out.write(raw_bytes)

    # Record stored document with course
    repo = get_teaching_repository()
    repo.save_document({
        "id": doc_id,
        "student_id": student_id,
        "original_filename": f.filename,
        "file_path": storage_path,
        "mime_type": f.mimetype or "application/octet-stream",
        "extension": val.extension or "",
        "file_size_bytes": val.file_size_bytes,
        "sha256_checksum": val.sha256_checksum or "",
        "detected_language": "en",
        "detected_title": os.path.splitext(f.filename)[0].replace("_", " ").title(),
        "detected_subject": subject_hint or "General",
        "course": course,
        "processing_state": "UPLOAD",
    })

    return jsonify({
        "success": True,
        "document_id": doc_id,
        "filename": val.sanitized_filename,
        "file_path": storage_path,
        "size_bytes": val.file_size_bytes,
        "course": course,
    }), 201


@documents_blueprint.route("/documents/pipeline-upload", methods=["POST"])
def pipeline_upload():
    """Executes the full 6-stage upload pipeline for educational files."""
    if "file" not in request.files:
        return jsonify({"error": "No 'file' provided in request."}), 400

    f = request.files["file"]
    raw_bytes = f.read()
    student_id = request.form.get("student_id") or "default_student"
    subject_hint = request.form.get("subject")
    course = request.form.get("course")

    try:
        result = _UPLOAD_PIPELINE.process_file_upload(
            raw_bytes=raw_bytes,
            original_filename=f.filename,
            mimetype=f.mimetype or "application/octet-stream",
            student_id=student_id,
            subject_hint=subject_hint,
            course=course,
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Upload pipeline failed: {str(e)}"}), 500


@documents_blueprint.route("/documents/direct-topic", methods=["POST"])
def direct_topic_ingest():
    """Processes a direct topic / syllabus request without requiring physical file upload."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    student_id = data.get("student_id", "default_student")
    if not topic or not topic.strip():
        return jsonify({"error": "Missing or empty 'topic' field in JSON."}), 400

    try:
        result = _UPLOAD_PIPELINE.process_direct_topic(topic=topic, student_id=student_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Direct topic processing failed: {str(e)}"}), 500



@documents_blueprint.route("/documents/process", methods=["POST"])
def process_document():
    """Extracts hierarchy, chunks, and indexes a stored document into the vector store."""
    data = request.get_json(silent=True) or {}
    file_path = data.get("file_path")
    doc_id = data.get("document_id") or f"doc_{uuid.uuid4().hex[:8]}"
    filename = data.get("filename") or os.path.basename(file_path or "doc.txt")
    requested_subject = data.get("subject")
    language = data.get("language", "en")

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"File not found at path: '{file_path}'"}), 400

    # Auto-classify subject if not provided or set to generic
    if not requested_subject or requested_subject.lower() in ("physics", "general", "default"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample_txt = f.read(2000)
            detected_sub, _ = _UNDERSTANDING_SERVICE.classify_subject_and_course(sample_txt, hint_title=filename)
            subject = requested_subject if requested_subject and requested_subject.lower() != "general" else detected_sub
        except Exception:
            subject = requested_subject or "Computer Science"
    else:
        subject = requested_subject

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

    # Perform educational content understanding
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_txt = f.read()
        understanding = _UNDERSTANDING_SERVICE.understand_content(
            text=full_txt,
            filename=filename,
            subject_hint=subject,
            source_reference=doc_id,
        )
        _UNDERSTANDINGS_STORE[doc_id] = understanding
    except Exception:
        pass

    return jsonify({
        "success": True,
        "document_id": doc_id,
        "title": structure.title,
        "subject": structure.subject,
        "total_chapters": len(structure.chapters),
        "total_chunks_indexed": len(chunks),
    })


@documents_blueprint.route("/documents/understand", methods=["POST"])
def understand_educational_content():
    """
    Analyzes uploaded material, raw text, or a direct topic to extract
    subject, course, concepts, prerequisites, definitions, and formulas.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    topic = data.get("topic", "")
    filename = data.get("filename")
    file_path = data.get("file_path")
    subject_hint = data.get("subject")

    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if not filename:
            filename = os.path.basename(file_path)

    if topic and not text:
        understanding = _UNDERSTANDING_SERVICE.understand_topic(topic, context=data.get("context"))
    elif text:
        understanding = _UNDERSTANDING_SERVICE.understand_content(text, filename=filename, subject_hint=subject_hint)
    else:
        return jsonify({"error": "Either 'text', 'topic', or a valid 'file_path' must be provided."}), 400

    return jsonify({
        "success": True,
        "understanding": understanding.model_dump()
    })


@documents_blueprint.route("/documents", methods=["GET"])
def list_student_documents():
    """Lists educational documents for a student with course filtering and keyword search."""
    student_id = request.args.get("student_id") or request.headers.get("X-Student-Id") or "default_student"
    
    # Phase 12C / 12D: Multi-student authorization check
    token = extract_token_from_request()
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")
        if caller_id and student_id and caller_id != student_id and payload.get("role") != "admin":
            return jsonify({
                "success": False,
                "error": f"Forbidden: You do not have permission to view student '{student_id}' documents.",
                "status": 403,
            }), 403

    course_filter = request.args.get("course")
    search_query = request.args.get("q", "").strip().lower()
    repo = get_teaching_repository()
    docs = repo.list_student_documents(student_id)

    if course_filter:
        docs = [
            d for d in docs
            if (d.get("course") or "").lower() == course_filter.lower()
            or (d.get("detected_subject") or "").lower() == course_filter.lower()
        ]
    if search_query:
        docs = [
            d for d in docs
            if search_query in (d.get("original_filename") or "").lower()
            or search_query in (d.get("detected_title") or "").lower()
            or search_query in (d.get("detected_subject") or "").lower()
            or any(search_query in (c.get("name") if isinstance(c, dict) else str(c)).lower() for c in d.get("concepts", []))
        ]

    return jsonify({
        "success": True,
        "student_id": student_id,
        "count": len(docs),
        "documents": docs,
    })


@documents_blueprint.route("/documents/<document_id>", methods=["DELETE"])
def delete_student_document(document_id: str):
    """Deletes an uploaded document and removes its file with strict ownership verification."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if not doc:
        return jsonify({"error": f"Document '{document_id}' not found or unauthorized."}), 404

    token = extract_token_from_request()
    caller_id = request.args.get("student_id") or request.headers.get("X-Student-Id")
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")

    # If caller identity is known, strictly forbid deleting another student's document
    doc_owner = doc.get("student_id")
    if caller_id and doc_owner and caller_id != doc_owner:
        if token:
            return jsonify({
                "success": False,
                "error": "Forbidden: You do not have permission to delete another student's document.",
                "status": 403,
            }), 403
        else:
            return jsonify({"error": f"Document '{document_id}' not found or unauthorized."}), 404

    deleted = repo.delete_document(document_id, student_id=caller_id)
    if not deleted:
        return jsonify({"error": f"Document '{document_id}' not found or unauthorized."}), 404
    return jsonify({"success": True, "deleted_document_id": document_id}), 200


@documents_blueprint.route("/documents/<document_id>/source", methods=["GET"])
def get_document_source(document_id: str):
    """Retrieves source text content and preview for student inspection."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if not doc:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404

    token = extract_token_from_request()
    caller_id = request.args.get("student_id") or request.headers.get("X-Student-Id")
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")

    doc_owner = doc.get("student_id")
    if caller_id and doc_owner and caller_id != doc_owner:
        return jsonify({
            "success": False,
            "error": "Forbidden: You do not have permission to inspect another student's document.",
            "status": 403,
        }), 403

    file_path = doc.get("file_path")
    content = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading document: {e}"

    return jsonify({
        "success": True,
        "document_id": document_id,
        "title": doc.get("detected_title") or doc.get("original_filename"),
        "filename": doc.get("original_filename"),
        "page_count": doc.get("page_count", 1),
        "course": doc.get("course"),
        "subject": doc.get("detected_subject"),
        "preview": content[:1500],
        "full_text": content,
    }), 200



@documents_blueprint.route("/documents/<document_id>", methods=["GET"])
def get_document_info(document_id: str):
    """Retrieves metadata for a processed document from repository or runtime store."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if doc:
        return jsonify({
            "success": True,
            "document_id": doc["id"],
            "student_id": doc["student_id"],
            "title": doc.get("detected_title") or doc.get("original_filename"),
            "original_filename": doc["original_filename"],
            "subject": doc.get("detected_subject"),
            "course": doc.get("course"),
            "chapter": doc.get("chapter"),
            "page_count": doc.get("page_count", 1),
            "processing_state": doc.get("processing_state", "READY"),
            "concepts_count": len(doc.get("concepts", [])),
            "concepts": [c.get("name") if isinstance(c, dict) else c for c in doc.get("concepts", [])],
            "uploaded_at": doc.get("uploaded_at"),
        })

    structure = _STRUCTURES_STORE.get(document_id)
    if not structure:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404
    return jsonify({
        "success": True,
        "document_id": structure.document_id,
        "title": structure.title,
        "subject": structure.subject,
        "total_pages": structure.total_pages,
        "language": structure.language,
        "total_chapters": len(structure.chapters),
    })


@documents_blueprint.route("/documents/<document_id>/status", methods=["GET"])
def get_document_status(document_id: str):
    """Retrieves processing state and progress for a document."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if not doc:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404
    return jsonify({
        "success": True,
        "document_id": doc["id"],
        "processing_state": doc.get("processing_state", "READY"),
        "title": doc.get("detected_title"),
        "subject": doc.get("detected_subject"),
        "concepts_count": len(doc.get("concepts", [])),
    })


@documents_blueprint.route("/documents/<document_id>/structure", methods=["GET"])
def get_document_structure(document_id: str):
    """Retrieves full chapter/section/concept hierarchy for a document."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if doc and doc.get("structure"):
        return jsonify({"success": True, "structure": doc["structure"]})

    structure = _STRUCTURES_STORE.get(document_id)
    if not structure:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404
    return jsonify({"success": True, "structure": structure.model_dump()})


@documents_blueprint.route("/documents/<document_id>/knowledge-graph", methods=["GET"])
def get_document_knowledge_graph(document_id: str):
    """Retrieves or synthesizes the grounded Educational Knowledge Graph for a document."""
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if doc:
        understanding_data = doc.get("understanding") or {}
        if isinstance(understanding_data, dict) and "knowledge_graph" in understanding_data:
            return jsonify({"success": True, "knowledge_graph": understanding_data["knowledge_graph"]})
        
        # Build if understanding present
        if understanding_data:
            u_obj = CourseUnderstanding(**understanding_data) if isinstance(understanding_data, dict) else None
            if u_obj:
                kg = KnowledgeGraphBuilder.build_from_understanding_and_chunks(u_obj, document_id=document_id)
                return jsonify({"success": True, "knowledge_graph": kg.model_dump()})

    return jsonify({"error": f"Knowledge graph not found for document '{document_id}'."}), 404


@documents_blueprint.route("/documents/knowledge-graph", methods=["POST"])
def generate_knowledge_graph():
    """Builds and returns an Educational Knowledge Graph from text, topic, or file path."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    text = data.get("text", "")
    subject_hint = data.get("subject")

    if not topic and not text:
        return jsonify({"error": "Either 'topic' or 'text' must be provided."}), 400

    if topic and not text:
        understanding = _UNDERSTANDING_SERVICE.understand_topic(topic)
    else:
        understanding = _UNDERSTANDING_SERVICE.understand_content(text, subject_hint=subject_hint)

    kg = KnowledgeGraphBuilder.build_from_understanding_and_chunks(
        understanding=understanding,
        chunks=[],
    )
    return jsonify({
        "success": True,
        "knowledge_graph": kg.model_dump(),
        "nodes_count": len(kg.nodes),
        "edges_count": len(kg.edges),
        "learning_path": kg.get_learning_path(),
    })


@documents_blueprint.route("/documents/<document_id>/concepts/<concept_name>/source-trace", methods=["GET"])
def get_concept_source_trace(document_id: str, concept_name: str):
    """
    Retrieves verifiable source grounding for any concept within an uploaded document.
    Returns exact page citation ('From your notes — Page X'), section, and excerpt.
    """
    repo = get_teaching_repository()
    doc = repo.get_document(document_id)
    if not doc:
        return jsonify({"error": f"Document '{document_id}' not found."}), 404

    # Search in retriever vector store
    results = _GLOBAL_RETRIEVER.vector_store.search_keyword(concept_name, top_k=5, document_id=document_id)
    if not results:
        try:
            vec = _GLOBAL_RETRIEVER.embedding_provider.get_embedding(concept_name)
            results = _GLOBAL_RETRIEVER.vector_store.search_semantic(vec, top_k=5, document_id=document_id)
        except Exception:
            results = []

    if results:
        best_chunk, score = results[0]
        page_num = best_chunk.page_number or 1
        return jsonify({
            "success": True,
            "trace_found": True,
            "concept": concept_name,
            "document_id": document_id,
            "source_title": doc.get("detected_title") or doc.get("original_filename"),
            "original_filename": doc.get("original_filename"),
            "page_number": page_num,
            "section": best_chunk.section_title or "Overview",
            "chapter": best_chunk.chapter_title,
            "citation": f"From your notes — Page {page_num}",
            "excerpt": best_chunk.content[:400],
            "score": round(score, 3),
        }), 200

    excerpt = doc.get("extracted_text", "")[:400] if doc.get("extracted_text") else f"Refer to {doc.get('original_filename')} for detailed exposition of {concept_name}."
    return jsonify({
        "success": True,
        "trace_found": True,
        "concept": concept_name,
        "document_id": document_id,
        "citation": f"From your notes — {doc.get('original_filename')}",
        "source_title": doc.get("detected_title") or doc.get("original_filename"),
        "page_number": doc.get("page_count", 1),
        "excerpt": excerpt,
    }), 200




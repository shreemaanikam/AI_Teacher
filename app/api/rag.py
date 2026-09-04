"""
Educational RAG REST API endpoints for Module 2.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.api.documents import _GLOBAL_RETRIEVER

rag_blueprint = Blueprint("rag_api", __name__)


@rag_blueprint.route("/rag/search", methods=["POST"])
def search_rag():
    """Performs hybrid retrieval for chunks related to an educational query."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query parameter cannot be empty."}), 400

    doc_id = data.get("document_id")
    top_k = int(data.get("top_k", 4))
    concept = data.get("concept")
    lang = data.get("language", "en")

    evidence = _GLOBAL_RETRIEVER.retrieve_evidence(
        query=query,
        target_concept=concept,
        document_id=doc_id,
        top_k=top_k,
        teaching_language=lang,
    )

    return jsonify({
        "success": True,
        "query": query,
        "grounding_level": evidence.grounding_level.value,
        "results_count": len(evidence.evidence_items),
        "results": [it.model_dump() for it in evidence.evidence_items],
    })


@rag_blueprint.route("/rag/evidence", methods=["POST"])
def get_evidence_package():
    """Generates a complete certified EvidencePackage for downstream Lesson Planning and Harness."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    concept = data.get("concept") or query
    if not query and not concept:
        return jsonify({"error": "Query or concept is required."}), 400

    doc_id = data.get("document_id")
    top_k = int(data.get("top_k", 3))
    lang = data.get("language", "en")

    evidence_pkg = _GLOBAL_RETRIEVER.retrieve_evidence(
        query=query or concept,
        target_concept=concept,
        document_id=doc_id,
        top_k=top_k,
        teaching_language=lang,
    )

    return jsonify({"success": True, "evidence_package": evidence_pkg.model_dump()})

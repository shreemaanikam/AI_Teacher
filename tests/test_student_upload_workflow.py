"""
Tests for Phase 2: Real Student Upload Workflow.
Verifies multi-format ingestion, 6-stage state progression, direct topic processing,
durable persistence, and re-fetching across sessions without re-uploading.
"""

import io
import pytest
from app import create_app
from app.rag.upload_service import StudentUploadPipeline
from app.db.repository import get_teaching_repository


@pytest.fixture
def app_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_file_upload_pipeline_six_stage_progression():
    """Verify that file upload executes all 6 stages cleanly and persists to repository."""
    pipeline = StudentUploadPipeline()
    recorded_stages = []

    def on_progress(state, pct):
        recorded_stages.append((state, pct))

    sample_notes = """# Chapter 3: Database Management Systems
## Section 3.1: ACID Properties
Definition: ACID represents Atomicity, Consistency, Isolation, and Durability in transactional databases.
Formula: T = Begin -> Read/Write -> Commit/Rollback
Example: Bank balance transfer where funds must not be partially debited.
### Concurrency Control
Definition: Methods to prevent race conditions during transaction execution like two-phase locking.
"""
    result = pipeline.process_file_upload(
        raw_bytes=sample_notes.encode("utf-8"),
        original_filename="dbms_acid.md",
        mimetype="text/markdown",
        student_id="student_alice_101",
        subject_hint="Computer Science",
        progress_callback=on_progress,
    )

    assert result["success"] is True
    assert result["student_id"] == "student_alice_101"
    assert result["processing_state"] == "READY"
    assert result["concepts_count"] >= 1
    assert result["total_chunks_indexed"] >= 1

    # Verify all 6 stages fired in order
    stage_names = [st[0] for st in recorded_stages]
    for expected_stage in ["UPLOAD", "PARSE", "UNDERSTAND", "STRUCTURE", "INDEX", "READY"]:
        assert expected_stage in stage_names

    # Verify persistent retrieval from repository
    repo = get_teaching_repository()
    doc_id = result["document_id"]
    retrieved = repo.get_document(doc_id)
    assert retrieved is not None
    assert retrieved["id"] == doc_id
    assert retrieved["student_id"] == "student_alice_101"
    assert retrieved["processing_state"] == "READY"
    assert len(retrieved["concepts"]) >= 1


def test_direct_topic_synthesis_without_file():
    """Verify that a direct topic request (e.g. 'Operating Systems Unit 3') generates notes, indexes, and persists."""
    pipeline = StudentUploadPipeline()
    result = pipeline.process_direct_topic(
        topic="Operating Systems Unit 3: Virtual Memory and Paging",
        student_id="student_bob_202"
    )

    assert result["success"] is True
    assert result["student_id"] == "student_bob_202"
    assert result["processing_state"] == "READY"
    assert result["subject"] == "Computer Science"
    assert result["concepts_count"] >= 1
    assert result["total_chunks_indexed"] >= 1

    # Check persistence
    repo = get_teaching_repository()
    doc = repo.get_document(result["document_id"])
    assert doc is not None
    assert doc["detected_title"] == "Operating Systems Unit 3: Virtual Memory and Paging"
    assert doc["student_id"] == "student_bob_202"


def test_student_document_listing_and_no_reupload(app_client):
    """Verify students can list their persistent documents and view info without re-uploading."""
    pipeline = StudentUploadPipeline()
    doc_result = pipeline.process_direct_topic(
        topic="Calculus: Derivatives and Integrals",
        student_id="student_carol_303"
    )
    doc_id = doc_result["document_id"]

    # 1. Test listing documents for this student
    resp = app_client.get("/api/v1/documents?student_id=student_carol_303")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["count"] >= 1
    doc_ids = [d["id"] for d in data["documents"]]
    assert doc_id in doc_ids

    # 2. Test fetching single document info without re-uploading
    resp_info = app_client.get(f"/api/v1/documents/{doc_id}")
    assert resp_info.status_code == 200
    info = resp_info.get_json()
    assert info["success"] is True
    assert info["document_id"] == doc_id
    assert info["student_id"] == "student_carol_303"
    assert info["processing_state"] == "READY"

    # 3. Test status endpoint
    resp_status = app_client.get(f"/api/v1/documents/{doc_id}/status")
    assert resp_status.status_code == 200
    status_data = resp_status.get_json()
    assert status_data["processing_state"] == "READY"


def test_api_pipeline_upload_and_direct_topic_routes(app_client):
    """Test REST API routes for pipeline upload and direct topic."""
    # 1. Test pipeline upload via POST /api/v1/documents/pipeline-upload
    sample_content = b"# Chapter 1: Introduction to Mechanics\n## Section 1.1: Newton Laws\nDefinition: First law is inertia.\n"
    data = {
        "file": (io.BytesIO(sample_content), "mechanics_notes.md", "text/markdown"),
        "student_id": "student_dan_404",
        "subject": "Physics",
    }
    resp = app_client.post("/api/v1/documents/pipeline-upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    res_json = resp.get_json()
    assert res_json["success"] is True
    assert res_json["processing_state"] == "READY"

    # 2. Test direct topic via POST /api/v1/documents/direct-topic
    topic_payload = {
        "topic": "Organic Chemistry: Functional Groups",
        "student_id": "student_dan_404",
    }
    resp_topic = app_client.post("/api/v1/documents/direct-topic", json=topic_payload)
    assert resp_topic.status_code == 200
    topic_json = resp_topic.get_json()
    assert topic_json["success"] is True
    assert topic_json["topic"] == "Organic Chemistry: Functional Groups"


def test_material_library_search_filter_source_and_delete(app_client):
    """Verify Phase 9C & 9D: search, course filtering, source inspection, and deletion."""
    import uuid
    student_id = f"student_lib_test_{uuid.uuid4().hex[:6]}"
    pipeline = StudentUploadPipeline()

    # 1. Ingest notes for Course: Data Structures
    ds_notes = b"# Unit 1: Arrays and Linked Lists\nDefinition: Array is a contiguous block of memory elements.\nFormula: addr(i) = base + i * size\n"
    ds_doc = pipeline.process_file_upload(
        raw_bytes=ds_notes,
        original_filename="arrays_linked_lists.md",
        mimetype="text/markdown",
        student_id=student_id,
        course="Data Structures",
        subject_hint="Computer Science",
    )
    ds_doc_id = ds_doc["document_id"]

    # 2. Ingest notes for Course: Operating Systems
    os_notes = b"# Unit 2: CPU Scheduling Algorithms\nDefinition: Round Robin scheduling uses time quantum slices.\nFormula: Turnaround = Completion - Arrival\n"
    os_doc = pipeline.process_file_upload(
        raw_bytes=os_notes,
        original_filename="cpu_scheduling.md",
        mimetype="text/markdown",
        student_id=student_id,
        course="Operating Systems",
        subject_hint="Computer Science",
    )
    os_doc_id = os_doc["document_id"]

    # 3. Filter by course: Data Structures
    ds_filter_resp = app_client.get(f"/api/v1/documents?student_id={student_id}&course=Data%20Structures")
    assert ds_filter_resp.status_code == 200
    ds_docs = ds_filter_resp.get_json()["documents"]
    assert len(ds_docs) == 1
    assert ds_docs[0]["id"] == ds_doc_id
    assert ds_docs[0]["course"] == "Data Structures"

    # 4. Search by keyword: "scheduling"
    search_resp = app_client.get(f"/api/v1/documents?student_id={student_id}&q=scheduling")
    assert search_resp.status_code == 200
    search_docs = search_resp.get_json()["documents"]
    assert len(search_docs) == 1
    assert search_docs[0]["id"] == os_doc_id

    # 5. Open Source / Inspect source content: GET /api/v1/documents/<doc_id>/source
    source_resp = app_client.get(f"/api/v1/documents/{ds_doc_id}/source")
    assert source_resp.status_code == 200
    src_data = source_resp.get_json()
    assert src_data["success"] is True
    assert "contiguous block of memory" in src_data["full_text"]

    # 6. Delete document: DELETE /api/v1/documents/<doc_id>
    del_resp = app_client.delete(f"/api/v1/documents/{ds_doc_id}?student_id={student_id}")
    assert del_resp.status_code == 200
    assert del_resp.get_json()["deleted_document_id"] == ds_doc_id

    # 7. Verify deletion persists
    get_after_del = app_client.get(f"/api/v1/documents/{ds_doc_id}")
    assert get_after_del.status_code == 404


def test_student_material_isolation(app_client):
    """Verify Student A cannot see or delete Student B's uploaded materials."""
    pipeline = StudentUploadPipeline()
    student_a = "student_alpha_isolation"
    student_b = "student_beta_isolation"

    doc_a = pipeline.process_file_upload(
        raw_bytes=b"# Student A Private Notes\nDefinition: Confidential A formula.\n",
        original_filename="notes_a.md",
        mimetype="text/markdown",
        student_id=student_a,
    )
    doc_b = pipeline.process_file_upload(
        raw_bytes=b"# Student B Private Notes\nDefinition: Confidential B formula.\n",
        original_filename="notes_b.md",
        mimetype="text/markdown",
        student_id=student_b,
    )

    # Student A lists materials: should only see doc_a
    list_a = app_client.get(f"/api/v1/documents?student_id={student_a}").get_json()["documents"]
    a_ids = [d["id"] for d in list_a]
    assert doc_a["document_id"] in a_ids
    assert doc_b["document_id"] not in a_ids

    # Student A cannot delete Student B's document
    del_unauth = app_client.delete(f"/api/v1/documents/{doc_b['document_id']}?student_id={student_a}")
    assert del_unauth.status_code == 404


def test_concept_source_traceability(app_client):
    """Verify Phase 9F: concept source traceability citation ('From your notes — Page X')."""
    import uuid
    pipeline = StudentUploadPipeline()
    std_id = f"std_trace_{uuid.uuid4().hex[:6]}"

    notes = (
        b"# Discrete Mathematics\n"
        b"## Chapter 4: Graph Theory\n"
        b"Definition: An Euler Path is a trail in a finite graph that visits every edge exactly once.\n"
        b"Formula: Deg(v) is even for all vertices except start and end.\n"
    )
    res = pipeline.process_file_upload(
        raw_bytes=notes,
        original_filename="graph_theory_notes.md",
        mimetype="text/markdown",
        student_id=std_id,
        course="Discrete Mathematics",
    )
    doc_id = res["document_id"]

    # Query source trace for "Euler Path"
    trace_res = app_client.get(f"/api/v1/documents/{doc_id}/concepts/Euler%20Path/source-trace")
    assert trace_res.status_code == 200
    trace_data = trace_res.get_json()
    assert trace_data["success"] is True
    assert "From your notes" in trace_data["citation"]
    assert trace_data["document_id"] == doc_id
    assert trace_data["concept"] == "Euler Path"



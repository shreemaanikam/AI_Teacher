"""
Tests for Phase 9B: Multi-Course & Multi-Subject Support.
Verifies a collegiate student can enroll in multiple distinct courses
(Data Structures, DBMS, Operating Systems, Mathematics, Machine Learning)
with separate units, concepts, exam dates, materials, and strict isolation.
"""

import uuid
import pytest
from app import create_app
from app.db.repository import get_teaching_repository
from app.learner.models import CourseDetail, CourseUnit


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_multi_course_enrollment_and_persistence(client):
    """Verify a single student can enroll in multiple distinct college courses."""
    repo = get_teaching_repository()
    student_id = f"std_{uuid.uuid4().hex[:6]}"

    # Create student profile first
    repo.save_learner_profile({
        "student_id": student_id,
        "name": "Aditya Rao",
        "college": "IIT Bombay",
        "department": "Computer Science and Engineering",
        "year": 2,
        "semester": 3,
    })

    # Enroll in Course 1: Data Structures
    c1 = repo.save_course({
        "student_id": student_id,
        "code": "CS201",
        "name": "Data Structures",
        "semester": 3,
        "exam_date": "2026-10-18",
        "target_score": "95%",
        "units": [
            {"title": "Linear Structures", "concepts": ["Arrays", "Linked Lists", "Stacks", "Queues"]},
            {"title": "Hierarchical Structures", "concepts": ["Trees", "Binary Search Trees", "Heaps"]},
        ],
        "concepts": ["Arrays", "Linked Lists", "Stacks", "Queues", "Binary Search Trees", "Heaps"],
    })

    # Enroll in Course 2: Database Management Systems
    c2 = repo.save_course({
        "student_id": student_id,
        "code": "CS301",
        "name": "Database Management Systems",
        "semester": 3,
        "exam_date": "2026-10-25",
        "target_score": "90%",
        "units": [
            {"title": "Relational Model", "concepts": ["Relational Algebra", "SQL", "Integrity Constraints"]},
            {"title": "Database Design", "concepts": ["Functional Dependencies", "Normalization", "B-Trees"]},
        ],
        "concepts": ["SQL", "Normalization", "Transactions", "B-Trees"],
    })

    # Enroll in Course 3: Operating Systems
    c3 = repo.save_course({
        "student_id": student_id,
        "code": "CS304",
        "name": "Operating Systems",
        "semester": 3,
        "exam_date": "2026-11-02",
        "target_score": "88%",
        "units": [
            {"title": "Process Management", "concepts": ["CPU Scheduling", "Deadlocks", "Semaphores"]},
            {"title": "Memory Management", "concepts": ["Virtual Memory", "Paging", "Page Replacement"]},
        ],
        "concepts": ["CPU Scheduling", "Deadlocks", "Virtual Memory", "Paging"],
    })

    # Verify student has all 3 courses
    courses = repo.list_student_courses(student_id)
    assert len(courses) == 3
    course_names = {c["name"] for c in courses}
    assert "Data Structures" in course_names
    assert "Database Management Systems" in course_names
    assert "Operating Systems" in course_names

    # Check course retrieval by ID
    loaded_c1 = repo.get_course(c1["id"])
    assert loaded_c1 is not None
    assert loaded_c1["code"] == "CS201"
    assert len(loaded_c1["units"]) == 2
    assert "Trees" in loaded_c1["units"][1]["concepts"]


def test_cross_student_course_isolation(client):
    """Verify Student A's courses are strictly isolated from Student B's courses."""
    repo = get_teaching_repository()
    student_a = f"std_a_{uuid.uuid4().hex[:6]}"
    student_b = f"std_b_{uuid.uuid4().hex[:6]}"

    repo.save_course({
        "student_id": student_a,
        "code": "CS201",
        "name": "Data Structures",
    })
    repo.save_course({
        "student_id": student_a,
        "code": "MATH202",
        "name": "Discrete Mathematics",
    })

    repo.save_course({
        "student_id": student_b,
        "code": "EE205",
        "name": "Analog Electronics",
    })

    courses_a = repo.list_student_courses(student_a)
    courses_b = repo.list_student_courses(student_b)

    assert len(courses_a) == 2
    assert len(courses_b) == 1
    assert all(c["student_id"] == student_a for c in courses_a)
    assert all(c["student_id"] == student_b for c in courses_b)
    assert not any(c["name"] == "Analog Electronics" for c in courses_a)
    assert not any(c["name"] == "Data Structures" for c in courses_b)


def test_courses_rest_api_lifecycle(client):
    """Test REST API routes: create course, list courses, view course detail with linked materials, and delete."""
    student_id = f"std_rest_{uuid.uuid4().hex[:6]}"
    doc_id = f"doc_{uuid.uuid4().hex[:6]}"

    # 1. POST /api/v1/courses (Create course)
    res = client.post("/api/v1/courses", json={
        "student_id": student_id,
        "name": "Machine Learning",
        "code": "CS405",
        "department": "Computer Science",
        "semester": 4,
        "exam_date": "2026-11-20",
        "target_score": "92%",
        "units": [
            {"title": "Supervised Learning", "concepts": ["Linear Regression", "Logistic Regression", "SVM"]},
            {"title": "Neural Networks", "concepts": ["Perceptrons", "Backpropagation", "Gradient Descent"]},
        ],
        "concepts": ["Linear Regression", "Logistic Regression", "Backpropagation", "Gradient Descent"],
    })
    assert res.status_code == 201
    c_data = res.get_json()
    assert c_data["success"] is True
    course_id = c_data["course"]["id"]
    assert c_data["course"]["name"] == "Machine Learning"

    # 2. GET /api/v1/courses?student_id=...
    list_res = client.get(f"/api/v1/courses?student_id={student_id}")
    assert list_res.status_code == 200
    courses = list_res.get_json()["courses"]
    assert len(courses) == 1
    assert courses[0]["id"] == course_id

    # 3. Save a document belonging to this course
    repo = get_teaching_repository()
    repo.save_document({
        "id": doc_id,
        "student_id": student_id,
        "original_filename": "ml_lecture_notes.pdf",
        "file_path": "/tmp/ml_lecture_notes.pdf",
        "mime_type": "application/pdf",
        "extension": ".pdf",
        "file_size_bytes": 1024,
        "sha256_checksum": "dummy_sha256",
        "course": "Machine Learning",
        "detected_subject": "Machine Learning",
        "processing_state": "READY",
    })

    # 4. GET /api/v1/courses/<id> (Detail + linked materials)
    detail_res = client.get(f"/api/v1/courses/{course_id}")
    assert detail_res.status_code == 200
    course_detail = detail_res.get_json()["course"]
    assert course_detail["materials_count"] == 1
    assert course_detail["materials"][0]["id"] == doc_id

    # 5. GET /api/v1/courses/<id>/materials
    mat_res = client.get(f"/api/v1/courses/{course_id}/materials")
    assert mat_res.status_code == 200
    assert mat_res.get_json()["count"] == 1

    # 6. DELETE /api/v1/courses/<id>
    del_res = client.delete(f"/api/v1/courses/{course_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["deleted_course_id"] == course_id

    # 7. Confirm 404 after deletion
    get_after = client.get(f"/api/v1/courses/{course_id}")
    assert get_after.status_code == 404

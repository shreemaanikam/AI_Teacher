"""
Courses & Subjects REST API endpoints for Phase 9B.
Allows college students to manage multi-course enrollments (e.g. Data Structures,
Operating Systems, DBMS, Mathematics) with units, concepts, exam dates, and materials.
"""

from __future__ import annotations
import uuid
from typing import Dict, Any
from flask import Blueprint, request, jsonify

from app.db.repository import get_teaching_repository
from app.auth.token_manager import extract_token_from_request, get_session_token_manager

courses_blueprint = Blueprint("courses_api", __name__)


@courses_blueprint.route("/courses", methods=["GET"])
def list_courses():
    """Lists courses enrolled by a student."""
    student_id = request.args.get("student_id")
    
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
                "error": f"Forbidden: You do not have permission to view student '{student_id}' courses.",
                "status": 403,
            }), 403

    repo = get_teaching_repository()

    if student_id:
        courses = repo.list_student_courses(student_id)
    else:
        # If student_id omitted, return for default_student or all
        courses = repo.list_student_courses("default_student")

    return jsonify({
        "success": True,
        "count": len(courses),
        "student_id": student_id or "default_student",
        "courses": courses,
    }), 200


@courses_blueprint.route("/courses", methods=["POST"])
def create_or_update_course():
    """Creates a new course or updates an existing course for a student."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing required field 'name' for course."}), 400

    student_id = data.get("student_id") or "default_student"
    code = data.get("code") or "".join([w[0].upper() for w in name.split()[:3]]) + "101"
    course_id = data.get("id") or data.get("course_id") or f"crs_{uuid.uuid4().hex[:8]}"

    course_payload = {
        "id": course_id,
        "course_id": course_id,
        "student_id": student_id,
        "code": code,
        "name": name,
        "department": data.get("department", "Computer Science"),
        "semester": int(data.get("semester", 1)),
        "description": data.get("description", f"Collegiate course on {name}"),
        "exam_date": data.get("exam_date"),
        "target_score": data.get("target_score", "90%"),
        "status": data.get("status", "ACTIVE"),
        "units": data.get("units", []),
        "concepts": data.get("concepts", []),
    }

    repo = get_teaching_repository()
    saved = repo.save_course(course_payload)

    # Also update student's profile enrolled_courses list if student exists
    profile = repo.get_learner_profile(student_id)
    if profile:
        existing_courses = profile.get("courses", [])
        if name not in existing_courses:
            existing_courses.append(name)
            profile["courses"] = existing_courses
            repo.save_learner_profile(profile)

    return jsonify({"success": True, "course": saved}), 201


@courses_blueprint.route("/courses/<course_id>", methods=["GET"])
def get_course_detail(course_id: str):
    """Retrieves detailed structure, units, concepts, and linked materials for a course."""
    repo = get_teaching_repository()
    course = repo.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404

    # Fetch materials linked to this course
    student_id = course["student_id"]
    all_docs = repo.list_student_documents(student_id)
    course_docs = [
        d for d in all_docs
        if d.get("course") == course["name"] or d.get("detected_subject", "").lower() == course["name"].lower()
    ]

    res = dict(course)
    res["materials_count"] = len(course_docs)
    res["materials"] = course_docs
    return jsonify({"success": True, "course": res}), 200


@courses_blueprint.route("/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id: str):
    """Deletes an enrolled course with strict ownership verification."""
    repo = get_teaching_repository()
    course = repo.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404

    token = extract_token_from_request()
    caller_id = request.args.get("student_id") or request.headers.get("X-Student-Id")
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")

    course_owner = course.get("student_id")
    if caller_id and course_owner and caller_id != course_owner:
        return jsonify({
            "success": False,
            "error": "Forbidden: You do not have permission to delete another student's course.",
            "status": 403,
        }), 403

    deleted = repo.delete_course(course_id)
    if not deleted:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404
    return jsonify({"success": True, "deleted_course_id": course_id}), 200


@courses_blueprint.route("/courses/<course_id>/materials", methods=["GET"])
def list_course_materials(course_id: str):
    """Lists all uploaded documents/notes for a specific course."""
    repo = get_teaching_repository()
    course = repo.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404

    student_id = course["student_id"]
    all_docs = repo.list_student_documents(student_id)
    course_docs = [
        d for d in all_docs
        if d.get("course") == course["name"] or d.get("detected_subject", "").lower() == course["name"].lower()
    ]
    return jsonify({
        "success": True,
        "course_id": course_id,
        "course_name": course["name"],
        "count": len(course_docs),
        "materials": course_docs,
    }), 200

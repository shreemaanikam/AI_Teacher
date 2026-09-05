"""
Authentication and Session REST API Endpoints for Phase 12.
Exposes endpoints for login, logout (with session revocation), token refresh, and session introspection.
"""

from __future__ import annotations
from flask import Blueprint, request, jsonify, g

from app.auth.token_manager import (
    get_session_token_manager,
    extract_token_from_request,
    require_auth,
)
from app.db.repository import get_teaching_repository

auth_blueprint = Blueprint("auth_api", __name__)


@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    """
    Authenticates a student and issues a cryptographically signed HMAC session pair.
    """
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id") or data.get("username")
    if not student_id:
        return jsonify({"success": False, "error": "Missing required field 'student_id'."}), 400

    role = data.get("role", "student")

    # Verify or initialize student profile in repository
    repo = get_teaching_repository()
    profile = repo.get_learner_profile(student_id)
    if not profile:
        profile = repo.save_learner_profile({
            "student_id": student_id,
            "id": student_id,
            "name": data.get("name") or student_id.replace("_", " ").title(),
            "email": data.get("email") or f"{student_id}@university.edu",
            "college": data.get("college", "University School of Engineering"),
            "degree": data.get("degree", "B.Tech Computer Science"),
            "semester": int(data.get("semester", 6)),
        })

    mgr = get_session_token_manager()
    session = mgr.create_session(student_id=student_id, role=role)

    return jsonify({
        "success": True,
        "message": "Authentication successful.",
        "student_id": student_id,
        "role": role,
        "profile": profile,
        **session,
    }), 200


@auth_blueprint.route("/auth/logout", methods=["POST"])
def logout():
    """
    Revokes the active session token, preventing replay attacks.
    """
    token = extract_token_from_request()
    if not token:
        # Also check json body
        data = request.get_json(silent=True) or {}
        token = data.get("token") or data.get("access_token")

    if not token:
        return jsonify({"success": False, "error": "Missing token to invalidate."}), 400

    mgr = get_session_token_manager()
    revoked = mgr.revoke_session(token)

    return jsonify({
        "success": True,
        "revoked": revoked,
        "message": "Session token successfully invalidated. Token cannot be reused.",
    }), 200


@auth_blueprint.route("/auth/refresh", methods=["POST"])
def refresh():
    """
    Exchanges a valid refresh token for a newly rotated access/refresh token pair.
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token") or extract_token_from_request()
    if not refresh_token:
        return jsonify({"success": False, "error": "Missing 'refresh_token' in payload."}), 400

    mgr = get_session_token_manager()
    new_session, err = mgr.refresh_session(refresh_token)
    if err or not new_session:
        return jsonify({
            "success": False,
            "error": f"Refresh failed: {err}",
            "status": 401,
        }), 401

    return jsonify(new_session), 200


@auth_blueprint.route("/auth/session", methods=["GET"])
@require_auth(strict=True)
def get_current_session():
    """
    Returns verified caller session details.
    Requires a valid, unexpired, unrevoked token.
    """
    student_id = getattr(g, "authenticated_student_id", None)
    payload = getattr(g, "session_payload", {}) or {}
    role = getattr(g, "user_role", "student")

    repo = get_teaching_repository()
    profile = repo.get_learner_profile(student_id) if student_id else None

    return jsonify({
        "success": True,
        "authenticated": True,
        "student_id": student_id,
        "role": role,
        "token_id": payload.get("jti"),
        "expires_at": payload.get("exp"),
        "profile": profile,
    }), 200

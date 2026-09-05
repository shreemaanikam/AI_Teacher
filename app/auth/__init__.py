"""Authentication module for AI Teacher Platform."""
from app.auth.token_manager import (
    SessionTokenManager,
    get_session_token_manager,
    require_auth,
    verify_student_ownership,
    extract_token_from_request,
)

__all__ = [
    "SessionTokenManager",
    "get_session_token_manager",
    "require_auth",
    "verify_student_ownership",
    "extract_token_from_request",
]

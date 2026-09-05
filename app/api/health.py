"""
Health & Diagnostics API endpoints for AI Teacher.
Provides safe connectivity verification across all cloud services, databases, and model providers.
"""

from __future__ import annotations
import os
import time
import requests
from flask import Blueprint, jsonify

from app.config import get_settings
from app.cache.redis_client import get_redis_client
from app.db.session import get_engine

health_blueprint = Blueprint("health_api", __name__)


@health_blueprint.route("/health", methods=["GET"])
def get_health_status():
    """
    Comprehensive health check endpoint.
    Distinguishes HEALTHY, DEGRADED, and UNAVAILABLE without leaking credentials.
    """
    db_status = "unavailable"
    cache_status = "fallback_memory"
    http_code = 200

    # 1. Database check
    try:
        engine = get_engine()
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        settings = get_settings()
        db_status = "connected_neon" if settings.database_url and "postgres" in settings.database_url else "connected_sqlite"
    except Exception:
        db_status = "unavailable"
        http_code = 503

    # 2. Cache check
    try:
        redis_client = get_redis_client()
        if redis_client.is_configured():
            cache_status = "connected_upstash" if redis_client.ping() else "failed_ping"
        else:
            cache_status = "fallback_memory_active"
    except Exception:
        cache_status = "fallback_memory_active"

    # Determine overall status
    if db_status.startswith("unavailable"):
        system_status = "UNAVAILABLE"
    elif db_status == "connected_neon" and cache_status == "connected_upstash":
        system_status = "HEALTHY"
    else:
        system_status = "DEGRADED"  # Operational with local fallbacks

    return jsonify({
        "status": "healthy" if system_status in ("HEALTHY", "DEGRADED") else "unavailable",
        "system_status": system_status,
        "timestamp": int(time.time()),
        "service": "ai-teacher-api",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "cache": cache_status,
        },
    }), http_code


@health_blueprint.route("/diagnostics", methods=["GET"])
def get_diagnostics():
    """
    Comprehensive diagnostics reporting connectivity across all providers.
    NEVER leaks API keys or secrets in responses.
    """
    settings = get_settings()
    diagnostics = {}

    # 1. Google Gemini
    if settings.gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.gemini_api_key}"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                diagnostics["gemini"] = "connected"
            elif res.status_code in (400, 401, 403):
                diagnostics["gemini"] = "unavailable"
            else:
                diagnostics["gemini"] = f"unavailable_http_{res.status_code}"
        except Exception:
            diagnostics["gemini"] = "fallback_active"
    else:
        diagnostics["gemini"] = "fallback_active"

    # 2. OpenAI
    if settings.openai_api_key:
        try:
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
            res = requests.get(url, headers=headers, timeout=3)
            diagnostics["openai"] = "connected" if res.status_code == 200 else f"error_http_{res.status_code}"
        except Exception:
            diagnostics["openai"] = "network_error"
    else:
        diagnostics["openai"] = "missing"

    # 3. Neon PostgreSQL
    if settings.database_url:
        try:
            engine = get_engine()
            with engine.connect() as conn:
                diagnostics["postgresql"] = "connected"
        except Exception as e:
            diagnostics["postgresql"] = f"connection_error: {str(e)[:40]}"
    else:
        diagnostics["postgresql"] = "missing (using local SQLite)"

    # 4. Upstash Redis
    redis_client = get_redis_client()
    if redis_client.is_configured():
        diagnostics["upstash_redis"] = "connected" if redis_client.ping() else "failed_ping"
    else:
        diagnostics["upstash_redis"] = "fallback_memory_active"

    # 5. Pinecone
    if settings.pinecone_api_key:
        try:
            host_url = settings.pinecone_host
            if host_url:
                if not host_url.startswith("http"):
                    host_url = f"https://{host_url}"
                headers = {"Api-Key": settings.pinecone_api_key}
                res = requests.post(f"{host_url}/describe_index_stats", headers=headers, timeout=3)
                diagnostics["pinecone"] = "connected" if res.status_code == 200 else f"error_http_{res.status_code}"
            else:
                diagnostics["pinecone"] = "configured_host_missing"
        except Exception:
            diagnostics["pinecone"] = "network_error"
    else:
        diagnostics["pinecone"] = "missing"

    # 6. Weaviate
    if settings.weaviate_url and settings.weaviate_api_key:
        try:
            url = f"{settings.weaviate_url.rstrip('/')}/v1/meta"
            headers = {"Authorization": f"Bearer {settings.weaviate_api_key}"}
            res = requests.get(url, headers=headers, timeout=3)
            diagnostics["weaviate"] = "connected" if res.status_code == 200 else f"error_http_{res.status_code}"
        except Exception:
            diagnostics["weaviate"] = "network_error"
    else:
        diagnostics["weaviate"] = "not_configured"

    # 7. Google Cloud Vision
    if settings.google_cloud_vision_api_key:
        try:
            url = f"https://vision.googleapis.com/v1/images:annotate?key={settings.google_cloud_vision_api_key}"
            payload = {"requests": [{"image": {"content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="}, "features": [{"type": "TEXT_DETECTION"}]}]}
            res = requests.post(url, json=payload, timeout=3)
            if res.status_code == 200:
                diagnostics["google_vision"] = "connected"
            elif res.status_code == 403:
                diagnostics["google_vision"] = "unavailable (billing_required)"
            else:
                diagnostics["google_vision"] = f"error_http_{res.status_code}"
        except Exception:
            diagnostics["google_vision"] = "network_error"
    else:
        diagnostics["google_vision"] = "missing"

    # 8. ElevenLabs
    if settings.elevenlabs_api_key:
        try:
            url = "https://api.elevenlabs.io/v1/user"
            headers = {"xi-api-key": settings.elevenlabs_api_key}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                diagnostics["elevenlabs"] = "connected"
            elif res.status_code == 401 or res.status_code == 400:
                diagnostics["elevenlabs"] = "authentication_failed"
            else:
                diagnostics["elevenlabs"] = f"error_http_{res.status_code}"
        except Exception:
            diagnostics["elevenlabs"] = "network_error"
    else:
        diagnostics["elevenlabs"] = "missing"

    # 9. D-ID
    if settings.did_api_key:
        try:
            url = "https://api.d-id.com/credits"
            headers = {"Authorization": f"Basic {settings.did_api_key}", "accept": "application/json"}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                rem = res.json().get("credits", [{}])[0].get("remaining", 0)
                diagnostics["did"] = f"connected ({rem} credits remaining)"
            else:
                diagnostics["did"] = f"error_http_{res.status_code}"
        except Exception:
            diagnostics["did"] = "network_error"
    else:
        diagnostics["did"] = "missing"

    # Overall system health
    is_ready = (
        diagnostics.get("gemini") == "connected" or diagnostics.get("openai") == "connected"
    ) and (
        diagnostics.get("postgresql") == "connected"
    ) and (
        diagnostics.get("pinecone") == "connected"
    )

    return jsonify({
        "success": True,
        "system_status": "READY" if is_ready else "PARTIALLY_READY",
        "providers": {
            "llm": settings.llm_provider,
            "embedding": settings.embedding_provider,
            "vector_db": settings.vector_db_provider,
            "ocr": settings.ocr_provider,
            "stt": settings.stt_provider,
            "tts": settings.tts_provider,
            "video": settings.video_provider,
        },
        "diagnostics": diagnostics,
    })

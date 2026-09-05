#!/usr/bin/env python3
"""
Production Process Manager and Launcher for Apurva AI Teacher.
Validates production configuration and boots the production WSGI server.
"""

import os
import sys
import socket
import subprocess
import signal
import multiprocessing

from app.config import Settings


def is_port_available(host: str, port: int) -> bool:
    """Checks if a socket can bind and listen on the given host/port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_sock:
            test_sock.settimeout(0.2)
            test_sock.connect((host, port))
            return False  # Already in use by an active listener
    except (OSError, ConnectionRefusedError):
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def select_port(host: str, desired_port: int) -> int:
    """Selects desired_port or searches alternative free ports if blocked."""
    if is_port_available(host, desired_port):
        return desired_port
    
    for alt_port in [5005, 8080, 8000, 5001]:
        if is_port_available(host, alt_port):
            return alt_port
    return desired_port


def validate_runtime_environment(settings: Settings) -> list[str]:
    """Validates configuration and returns any critical warnings."""
    warnings = []
    if settings.app_env.lower() == "production":
        if not settings.gemini_api_key and not settings.openai_api_key:
            warnings.append("No primary or secondary LLM key found (GEMINI_API_KEY or OPENAI_API_KEY).")
        if not settings.database_url:
            warnings.append("DATABASE_URL is not configured; running on persistent SQLite fallback.")
        if not settings.upstash_redis_rest_url:
            warnings.append("UPSTASH_REDIS_REST_URL not configured; running on in-memory cache.")
        if not settings.pinecone_api_key:
            warnings.append("PINECONE_API_KEY not configured; running on hybrid keyword/semantic fallback.")
    return warnings


def main():
    settings = Settings.from_env()
    warnings = validate_runtime_environment(settings)
    
    requested_host = os.environ.get("HOST", "127.0.0.1")
    requested_port = int(os.environ.get("PORT", 5001))
    
    port = select_port(requested_host, requested_port)
    host = requested_host

    # Calculate recommended workers: (2 * cores) + 1 (capped between 2 and 8)
    cpu_count = multiprocessing.cpu_count() or 2
    default_workers = max(2, min(cpu_count * 2 + 1, 8))
    workers = int(os.environ.get("WORKERS", default_workers))
    timeout = int(os.environ.get("TIMEOUT", 60))
    
    print("=" * 68)
    print("🚀 APURVA AI TEACHER — PRODUCTION WSGI SERVER")
    print(f"🌍 Environment   : {settings.app_env.upper()}")
    print(f"👥 Workers       : {workers}")
    print(f"🔗 Bind Address  : http://{host}:{port}")
    print(f"⏱️ Request Timeout: {timeout}s")
    if port != requested_port:
        print(f"⚠️ Port {requested_port} occupied. Auto-routed to free port: {port}")
    if warnings:
        print("⚠️  Configuration Notices:")
        for w in warnings:
            print(f"    - {w}")
    print("=" * 68)

    # Check if gunicorn is available for current Python interpreter
    has_gunicorn = False
    try:
        import gunicorn  # noqa: F401
        has_gunicorn = True
    except ImportError:
        has_gunicorn = False

    if has_gunicorn:
        cmd = [
            sys.executable, "-m", "gunicorn",
            "-w", str(workers),
            "-b", f"{host}:{port}",
            "--timeout", str(timeout),
            "--graceful-timeout", "30",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "wsgi:application"
        ]
        try:
            proc = subprocess.Popen(cmd)

            def handle_signal(sig, frame):
                print(f"\n[Production Manager] Received signal {sig}. Initiating graceful shutdown...")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                sys.exit(0)

            signal.signal(signal.SIGTERM, handle_signal)
            signal.signal(signal.SIGINT, handle_signal)
            proc.wait()
            return
        except Exception as e:
            print(f"[Production Manager] Gunicorn startup error: {e}")

    # Direct WSGI runner fallback
    print(f"[Production Manager] Running WSGI application on http://{host}:{port}...")
    from wsgi import application
    application.run(host=host, port=port)


if __name__ == "__main__":
    main()

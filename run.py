import os
import socket
import sys
from app import create_app
from app.config import Settings

settings = Settings.from_env()
app = create_app(settings)

def is_port_available(host: str, port: int) -> bool:
    """Checks if a socket can bind and listen on the given host/port and isn't intercepted by AirPlay."""
    # First check if another service (like macOS AirPlay) is already actively listening
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_sock:
            test_sock.settimeout(0.2)
            test_sock.connect((host, port))
            return False  # Already in use by an active listener
    except (OSError, ConnectionRefusedError):
        pass

    # Then check if we can bind
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

if __name__ == "__main__":
    requested_port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    
    port = select_port(host, requested_port)
    if port != requested_port:
        print(f"⚠️ Port {requested_port} is occupied (common on macOS due to AirPlay Receiver / ControlCenter).")
        print(f"🔄 Auto-routing to free port: {port}")
        print(f"💡 Tip to free port 5000 on macOS: System Settings -> General -> AirDrop & AirPlay -> Turn AirPlay Receiver OFF\n")
    
    print("=" * 65)
    print(f"🎓 APURVA AI TEACHER — PRODUCTION HACKATHON SERVER")
    print(f"👉 Canonical Demo URL : http://{host}:{port}/demo")
    print(f"👉 Root URL           : http://{host}:{port}/")
    print(f"👉 Diagnostics API    : http://{host}:{port}/api/v1/diagnostics")
    print(f"👉 Health Check       : http://{host}:{port}/api/v1/health")
    print("=" * 65)
    
    app.run(host=host, port=port, debug=False)

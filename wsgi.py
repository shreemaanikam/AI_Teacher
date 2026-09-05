"""
WSGI entrypoint for production deployment of Apurva AI Teacher.
Serves the Flask application through Gunicorn or any PEP 3333 compliant WSGI server.
"""

import os
from app import create_app
from app.config import Settings

# Initialize application using environment-derived settings
settings = Settings.from_env()
application = create_app(settings)
app = application  # Standard WSGI alias

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "0.0.0.0")
    application.run(host=host, port=port)

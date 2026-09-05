# =================================================================
# Stage 1: Build Frontend Single Page Application
# =================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install

COPY frontend/ ./
RUN npm run build

# =================================================================
# Stage 2: Production Python WSGI Application Container
# =================================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5001 \
    HOST=0.0.0.0 \
    APP_ENV=production

WORKDIR /app

# Install runtime dependencies for psycopg2 and audio tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY app/ ./app/
COPY wsgi.py run_production.py run.py ./
COPY scripts/ ./scripts/
COPY public/ ./public/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist/ ./frontend/dist/
RUN cp -rf ./frontend/dist/assets/* ./app/static/assets/ 2>/dev/null || true && \
    cp -f ./frontend/dist/index.html ./app/templates/demo.html 2>/dev/null || true

# Setup non-root user and persistent storage permissions
RUN useradd -m -u 1001 appuser && \
    mkdir -p data/uploads data/backups && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-5001}/api/v1/diagnostics || curl -f http://127.0.0.1:${PORT:-5001}/api/v1/health || exit 1

CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT:-5001} --timeout 120 --access-logfile - --error-logfile - wsgi:application"]

# Apurva AI Teacher — Production Deployment & Infrastructure Runbook

This document details the production deployment architecture, infrastructure hardening, disaster recovery runbooks, zero-leakage security protocols, and incident response procedures for the **Apurva AI Teacher** platform.

---

## 1. Prerequisites & System Requirements

### Host Environment
- **Operating System**: macOS (13+ Ventura / Sonoma / Sequoia) or Linux (Ubuntu 22.04 LTS+, Debian 12+, RHEL 9+)
- **Python**: Version 3.10, 3.11, or 3.12 (CPython runtime)
- **Node.js**: Node 18.x, 20.x, or 22.x LTS with `npm` 9.x+
- **RAM**: Minimum 4 GB (8 GB recommended for concurrent video and AST sandbox execution)
- **Disk Space**: Minimum 2 GB free space for uploads, SQLite database, and audio cache
- **Network Ports**:
  - `5001`: Production WSGI Application Port (Gunicorn)
  - `5000`: Local Development Flask Server Port
  - `5173`: Local Vite Development Server Port (Frontend)

---

## 2. Clone & Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/shreemaanikam/AI_Teacher.git
cd AI_Teacher

# 2. Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install and build frontend assets
cd frontend
npm ci
npm run build
cd ..
```

---

## 3. Environment Variables Specification

The application loads configuration via `app/config.py` using `.env`. A sanitized reference template is provided in `.env.example` and `.env.production.example`.

### Key Environment Variables

| Variable | Description | Production Default / Example | Resilient Fallback if Omitted |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Application environment mode | `production` | Defaults to `development` |
| `SECRET_KEY` | Cryptographic session signing key | `secure-random-64-char-hex` | High-entropy auto-generated key |
| `DATABASE_URL` | Neon PostgreSQL pooled connection URI | `postgresql://user:pass@ep-pooler.aws.neon.tech/neondb?sslmode=require` | Auto-switches to local SQLite (`data/ai_teacher.db`) |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis REST endpoint | `https://your-upstash-redis.upstash.io` | Auto-switches to local thread-safe memory cache |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis REST authorization token | `token_string` | Local in-memory cache |
| `GEMINI_API_KEY` | Google Gemini AI API key | `AIzaSy...` | Routes to OpenAI or Deterministic Harness |
| `GEMINI_MODEL` | Gemini LLM model identifier | `gemini-2.5-flash` | `gemini-2.5-flash` or fallback |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | Deterministic Teaching Harness |
| `PINECONE_API_KEY` | Pinecone vector index API key | `pcsk_...` | Local dense cosine vector store |
| `PINECONE_INDEX_NAME` | Pinecone index name | `apurva-ai-teacher` | Local vector index |
| `ELEVENLABS_API_KEY` | ElevenLabs neural voice synthesis API key | `xi-...` | Local 24kHz studio PCM synthesis |
| `DID_API_KEY` | D-ID video & avatar API key | `basic_auth_key` | High-fidelity Procedural Presenter engine |

> [!IMPORTANT]
> Never commit real secrets to source control. Client bundles are scanned during build to guarantee zero client-side secret exposure.

---

## 4. Database Setup & Migrations (PostgreSQL / SQLite Fallback)

### Architecture
The database layer (`app/db/session.py`) implements a resilient **Dual-Engine Architecture**:
1. **Primary**: Managed cloud PostgreSQL (Neon Serverless with PgBouncer connection pooling).
2. **Autonomous Fallback**: Persistent SQLite at `data/ai_teacher.db`.

If PostgreSQL connection fails due to network partitions, host lookup errors, or connection pool exhaustion, the connection manager intercepts the error, logs a clean warning, and seamlessly switches the active SQLAlchemy session factory to SQLite.

### Database Tables & Schema
- `users`: User profiles, roles, and cryptographic password hashes.
- `students`: Student identity, target languages, learning velocity, and cognitive profiles.
- `courses`: Academic courses (e.g., AD5305 Machine Learning, PH101 Physics).
- `course_documents`: Course syllabus, lecture notes, textbook chapters, and AST chunks.
- `lesson_plans`: Structured lesson timelines, pedagogical strategies, and time budgets.
- `doubts`: Student doubt vault, contextual bookmarks, timestamps, and resolved answers.
- `homework_tasks`: Adaptive assignments, coding drills, and multi-point rubrics.
- `student_submissions`: Code and text submissions, rubric evaluation scores, and feedback.
- `exam_plans`: 5-unit exam study schedules, daily tasks, and replanned states.
- `learning_events`: Comprehensive audit log of all pedagogical and telemetry events.

---

## 5. Redis & Caching Architecture (Upstash Redis / In-Memory Fallback)

The caching service (`app/cache/service.py`):
1. **Primary**: Upstash Redis via REST API, optimized for serverless environments.
2. **Fallback**: Thread-safe in-memory LRU cache with per-key TTL eviction.

### Cached Subsystems
- User session authentication tokens.
- Frequent RAG embedding queries and top-k chunk retrievals.
- Synthesized audio audio-fingerprints (prevents redundant TTS billing).
- Student cognitive mastery snapshots.

---

## 6. Vector DB & Knowledge Graph (Pinecone / Local Hybrid Fallback)

### Dual Vector Storage
- **Primary**: Pinecone Serverless Index with 1024-dimensional cosine metric.
- **Local Fallback**: `app/rag/vector_store.py` includes an in-memory NumPy/math dense cosine similarity engine paired with BM25 keyword filtering for zero-dependency retrieval.

### Concept Knowledge Graph
- Located at `app/rag/knowledge_graph.py`.
- Constructs directional Directed Acyclic Graphs (DAGs) of syllabus topics.
- Tracks prerequisites (e.g., `Linear Algebra` $\rightarrow$ `PCA`, `Gradient Descent` $\rightarrow$ `Neural Networks`).
- Ensures students are taught prerequisites before complex downstream concepts.

---

## 7. AI Model Providers & Router Configuration

The platform utilizes a **Three-Tier LLM Router** (`app/router/router.py`):

1. **Tier 1 (Primary)**: Google Gemini 2.5 Flash (`gemini-2.5-flash`). Delivers high reasoning speed, 1M context support, and cost-effective generation.
2. **Tier 2 (Cloud Fallback)**: OpenAI GPT-4o (`gpt-4o`). Automatically activated on Gemini HTTP 429 quota exhaustion or API failure.
3. **Tier 3 (Deterministic Teaching Harness)**: `app/harness/orchestrator.py` provides 100% offline, guaranteed pedagogical responses using verified syllabi and cognitive templates.

---

## 8. Voice & Audio Generation (ElevenLabs / Local 24kHz Engine)

### Audio Delivery Pipeline
- **Primary**: ElevenLabs Neural Text-to-Speech (`eleven_multilingual_v2`) using the custom collegiate voice profile.
- **Local Fallback**: Local 24kHz studio PCM waveform synthesis (`app/media/tts/local_tts.py`) or platform-native speech synthesis (`macOS say`).
- **Audio Format**: Mono 24,000 Hz, 16-bit linear PCM or MP3, optimized for web streaming.
- **Audio Caching**: SHA-256 fingerprinting on text + language ensures identical sentences are never re-synthesized.

---

## 9. Avatar & Video System (D-ID Cloud API / Procedural Presenter Fallback)

### Two-Tier Avatar Architecture
- **Tier 1 (Cloud Video)**: D-ID Talk Streaming API (`app/media/avatar/did_avatar.py`) produces photorealistic video streams from uploaded teacher stills.
- **Tier 2 (Procedural Presenter)**: `app/media/avatar/canvas_avatar.py` & `procedural_avatar.py`.
  - Zero-latency client-side Canvas and SVG rendering.
  - 9 expressive pedagogical states: `IDLE`, `SPEAKING`, `EXPLAINING`, `THINKING`, `LISTENING`, `CELEBRATING`, `CONFUSED`, `EMPHASIZING`, `ENCOURAGING`.
  - Realistic physical movements: natural blinking (every 3-5s), subtle head nodding, and dynamic lip synchronization mapped to audio amplitude envelopes.

---

## 10. Frontend Production Build & Asset Serving

### Technologies
- **Framework**: React 19 + TypeScript
- **Styling**: Tailwind CSS with custom academic dark/light themes
- **Icons**: Lucide React
- **Build Tool**: Vite 8.2

### Build Commands
```bash
cd frontend
npm ci
npm run build
```
Build outputs are compiled into `frontend/dist/` (`index.html`, minified JavaScript, and CSS bundles). In production, these static assets are served directly via Flask WSGI or an Nginx reverse proxy.

---

## 11. Gunicorn WSGI & Process Management

### Production Process Manager (`run_production.py`)
```bash
python3 run_production.py
```
This script validates configuration, checks database connectivity, ensures frontend production builds exist, and spawns Gunicorn with:
- **Workers**: 4 worker processes (`multiprocessing.cpu_count() * 2 + 1`)
- **Worker Class**: `sync` (or `gthread` with 2 threads per worker)
- **Bind**: `0.0.0.0:5001`
- **Timeout**: 120 seconds (for handling document RAG parsing)
- **Access Logs**: Structured JSON with `X-Request-ID` tracking

---

## 12. Docker & Containerized Orchestration

### Dockerfile
A multi-stage container build packaging Node frontend compilation and Python backend runtime:
```dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
EXPOSE 5001
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5001", "wsgi:app"]
```

### Docker Compose
```bash
docker compose up -d --build
docker compose ps
docker compose logs -f ai-teacher
```

---

## 13. Health Checks & Synthetic Monitoring

The system exposes standardized health probes:
- `GET /api/v1/health`: Overall system readiness and component statuses.
- `GET /api/v1/health/liveness`: Process liveness probe for Kubernetes / Docker restarts.
- `GET /api/v1/health/readiness`: Verifies database and cache readiness.

### Sample Health Response
```json
{
  "status": "HEALTHY",
  "version": "1.0.0",
  "timestamp": "2026-09-04T23:10:20Z",
  "components": {
    "database": {"status": "UP", "engine": "sqlite_fallback"},
    "cache": {"status": "UP", "provider": "in_memory"},
    "model_router": {"status": "UP", "primary": "gemini-2.5-flash"},
    "voice_engine": {"status": "UP", "tts": "local_studio_pcm"},
    "avatar_engine": {"status": "UP", "engine": "procedural_presenter"}
  }
}
```

---

## 14. Backup & Disaster Recovery Protocols

### Automatic Database Backup
```bash
python3 scripts/backup_db.py
```
Outputs atomic backups to `data/backups/`:
- `backup_YYYYMMDD_HHMMSS.json`
- `backup_YYYYMMDD_HHMMSS.db`
- `backup_YYYYMMDD_HHMMSS_manifest.json` with SHA-256 checksums.

### Verification & Restore Procedure
```bash
# Dry run verification
python3 scripts/restore_db.py --latest --dry-run

# Actual atomic restoration
python3 scripts/restore_db.py --latest
```

---

## 15. Failure Domains & Graceful Degradation Matrix

| Domain | Detection | Automatic Fallback | Recovery Procedure |
| :--- | :--- | :--- | :--- |
| **1. Database** | Connection timeout / 503 | Auto-switches to local SQLite (`data/ai_teacher.db`) | Check Neon status dashboard; reconnect pool; run `restore_db.py`. |
| **2. Redis Cache** | REST ping 403/5xx | Auto-switches to thread-safe in-memory cache | Verify Upstash token; restart cache client. |
| **3. Vector DB** | Pinecone API timeout | Local NumPy dense cosine similarity + BM25 | Check Pinecone status; re-index via RAG pipeline. |
| **4. Primary LLM** | Gemini 429 quota / 500 error | Auto-routes to OpenAI GPT-4o or Teaching Harness | Monitor Google Cloud quotas; replenish API credits. |
| **5. Voice / TTS** | ElevenLabs credit limit | 24kHz Studio PCM / local platform speech | Renew ElevenLabs plan; audio cache preserves past clips. |
| **6. Avatar / Video** | D-ID credit depletion | Procedural Presenter engine with Canvas lip sync | Replenish D-ID credits; procedural avatar requires 0 credits. |
| **7. Media Storage** | Disk space / write error | In-memory stream buffer with temporary cleanup | Purge expired temp files in `data/uploads/`. |
| **8. Process Crash** | Container exit / SIGSEGV | Gunicorn auto-spawns replacement worker process | Inspect Gunicorn error log; trace `X-Request-ID`. |

---

## 16. Security Invariants & Hardening Verification

1. **Zero Client-Side Secrets**: All API tokens remain backend-only. Frontend builds contain zero credentials.
2. **Multi-Student IDOR Defense**: All student data endpoints enforce strict ownership checks; cross-student query attempts return `403 Forbidden`.
3. **AST Sandbox Security**: Practical code execution runs in an Abstract Syntax Tree (AST) sandbox that strictly whitelists safe mathematical operations and blocks dangerous modules (`os`, `sys`, `subprocess`, `open`, `__import__`).
4. **Rate Limiting & Payload Caps**: File uploads are capped at 50 MB with magic byte inspection (`%PDF`, `PK\x03\x04`).
5. **Sanitized Logs**: Error logs and diagnostic endpoints redact keys, passwords, and personal student information.

---

## 17. Rollback & Incident Response Procedures

### Rollback Runbook
If an unexpected defect occurs in a production release:
1. **Container Rollback**:
   ```bash
   docker compose down
   docker tag ai-teacher:previous ai-teacher:latest
   docker compose up -d
   ```
2. **Database Rollback**:
   ```bash
   python3 scripts/restore_db.py --latest
   ```
3. **Frontend Invalidation**:
   Purge CDN or browser caches by deploying an incremented asset hash version via Vite.

# 🎓 Aster AI — Your Personal AI College Teacher

**Autonomous Multi-Course College AI Educator • Upload-Driven • Multimodal Adaptive Platform**

[![Test Suite](https://img.shields.io/badge/pytest-422%20passed%20(100%25)-brightgreen.svg)](tests)
[![Release Gates](https://img.shields.io/badge/release%20certification-18%2F18%20gates%20PASS-brightgreen.svg)](docs/FINAL_RELEASE_VERIFICATION.md)
[![Frontend](https://img.shields.io/badge/frontend-React%2019%20%7C%20TailwindCSS%20%7C%20Vite-blue.svg)](frontend)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](requirements.txt)
[![Security](https://img.shields.io/badge/security-0%20client%20secrets%20%7C%20AST%20sandbox-green.svg)](app/security)

Apurva AI Teacher is an autonomous, upload-driven, multi-course college AI educator engineered to teach authentic university engineering subjects. Rather than serving as a generic chatbot or single-topic demonstrator, Apurva ingests real university course materials (lecture notes, syllabi, problem sets), builds concept dependency graphs, computes principled study schedules for upcoming exams, generates adaptive homework with rubric evaluations, solves multi-turn student doubts with contextual memory, supports live video interruption and resumption, and executes pedagogical teaching controls with a realistic human avatar teacher.

---

## 🌟 Key Capabilities & Architectural Highlights

- **🧠 Authentic 5-Unit Machine Learning Course (AD5305 / CS4403)**: Ingested and certified on actual collegiate materials from Chennai Institute of Technology across all 5 units:
  - *Unit 1*: Machine Learning Foundations & Supervised Learning (Linear & Polynomial Regression, Normal Equations).
  - *Unit 2*: Classification & Neural Networks (Logistic Regression, Decision Trees, Multilayer Perceptrons, Backpropagation).
  - *Unit 3*: Unsupervised Learning & Dimensionality Reduction (K-Means Clustering, PCA, SVD, Expectation-Maximization).
  - *Unit 4*: Probabilistic & Ensemble Learning (Naive Bayes, Random Forests, AdaBoost, Gradient Boosting).
  - *Unit 5*: Reinforcement Learning & Deep Architectures (Markov Decision Processes, Q-Learning, CNNs, Sequence Models).
  - *100% source provenance with verified mathematical proofs.*
- **🏠 Personalized Student Home Dashboard**: Dynamically answers *"What should I study now?"*, tracks multi-course exam countdowns, calculates principled readiness percentages, and monitors daily study tasks.
- **🗓️ Dependency-Aware Exam Planner & Dynamic Replanning**: Automatically calculates day-by-day study schedules tailored to student mastery, available daily hours, and upcoming exam dates, dynamically replanning when tasks are missed.
- **📝 Adaptive Homework & Subject Practical Tasks**: Generates tailored assignments, Python ML code debugging drills, ANSI SQL queries for DBMS, and BST traversals evaluated against multi-point rubrics.
- **🛡️ Secure AST Python Sandbox**: Safely executes student numerical algorithms and mathematical proofs while strictly blocking system exploits (`os`, `sys`, `subprocess`, `open`).
- **🙋‍♀️ Ask Teacher & Contextual Memory**: Understands colloquial follow-ups (*"Explain that again"*, *"Why was that negative?"*) without restating context; maintains persistent student Doubt Vaults.
- **⏸️ Sub-Second Video Interruption & Resume**: Pauses teaching sessions on student doubts, resolves questions with avatar cues, and resumes video at the exact interrupted timestamp.
- **🎛️ Real Pedagogical Teaching Controls**: Real-time backend execution for *"Explain simpler"*, *"Another example"*, *"Show visually"*, *"Give hint"*, *"Slow down"*, and language switching to Hindi (`hi`) or Tamil (`ta`).
- **🎭 Human AI Teacher Avatar**: 9 expressive pedagogical states (`EXPLAINING`, `THINKING`, `LISTENING`, `CELEBRATING`, `ENCOURAGING`, etc.) with dynamic lip-sync, blinking, and head gestures.
- **🔒 Multi-Tenant Data Isolation & Zero-Leakage Security**: Absolute student data boundaries across profiles, uploaded documents, RAG vectors, and assignments. Zero hardcoded credentials in version control.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x, 20.x, or 22.x LTS with `npm`
- **Virtual environment**: `venv` or `conda`

### 2. Clone & Setup
```bash
# Clone repository
git clone https://github.com/shreemaanikam/AI_Teacher.git
cd AI_Teacher

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Build production frontend
cd frontend
npm ci
npm run build
cd ..
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(All external providers have verified deterministic local fallbacks, allowing offline or partial-credential execution with zero crashes).*

### 4. Running the Platform

#### Mode A: Production WSGI Server (Recommended for Evaluation & Demo)
```bash
python3 run_production.py
```
Spawns the hardened Gunicorn WSGI server on **`http://localhost:5001/`** with 4 workers and pre-built React 19 frontend assets.

#### Mode B: Development Mode (Hot Reloading)
```bash
# Terminal 1: Backend
python3 run.py  # Runs on http://localhost:5000/

# Terminal 2: Frontend
cd frontend
npm run dev     # Runs on http://localhost:5173/
```

Open `http://localhost:5173`. Vite proxies `/api` to Flask on port 5000.

#### Mode C: Docker Containerization
```bash
docker compose up -d --build
```

#### Mode D: Production Cloud Deployment (Render Blueprint)
Deploy the unified Python WSGI + React 19 single-page application to Render with zero manual build steps:
1. Connect your GitHub repository to [Render.com](https://render.com).
2. Create a new **Web Service** or select **Blueprints** and point to `render.yaml`.
3. Set environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `APP_ENV`: `production`
   - `LLM_PROVIDER`: `gemini`
   - `DATABASE_URL`: (Optional) Neon PostgreSQL connection string (defaults to local SQLite if unset).
4. Build Command: `pip install --no-cache-dir -r requirements.txt && cd frontend && npm install && npm run build && cd .. && cp frontend/dist/assets/* app/static/assets/ && cp frontend/dist/index.html app/templates/demo.html`
5. Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 wsgi:application`
6. Health Check Path: `/api/v1/health`


---

## 🎯 Primary Demo & Hackathon Workflow

Open your browser to:
### **[http://localhost:5001/](http://localhost:5001/)**

### 7-Stage Interactive Judging Workflow:
1. **Stage 1 (Student Dashboard & Subject Choice)**: Select course (e.g. *AD5305: Machine Learning* or *PH101: Engineering Physics*), view syllabus breakdown, and inspect exam countdowns.
2. **Stage 2 (Upload-Driven RAG & Knowledge Graph)**: Ingest university PDFs with AST formula extraction, concept DAG generation, and vector indexing.
3. **Stage 3 (AI Lesson Plan)**: Dynamic pedagogical planning with time-budgeted concept exposition and Bloom taxonomy checkpoints.
4. **Stage 4 (Multimodal Classroom)**: Real-time SVG whiteboard, interactive human avatar teacher, neural speech, and synchronized subtitles.
5. **Stage 5 (Live Interruption & Doubt Resolution)**: Raise hand or ask doubt mid-sentence; avatar pauses, resolves the doubt using syllabus context, and resumes at the exact second.
6. **Stage 6 (Misconception Diagnosis & AST Practical Lab)**: Detect student misunderstandings, switch teaching strategy, and execute safe Python code drills.
7. **Stage 7 (Exam Planner & Analytics)**: Review dynamic 5-unit study plan, Bloom mastery radar chart, and inspect real-time system telemetry via the **"🛠️ Telemetry"** button.

---

## 🧪 Comprehensive Automated Verification (399 / 399 Tests Passing)

The entire platform is covered by a 24-suite regression test framework guaranteeing pedagogical accuracy, API contracts, security invariants, and runtime resilience:

```bash
# Run the complete test suite (399 tests passing in ~70s)
python3 -m pytest tests/ -v

# Run the 5-run master demo stress rehearsal
python3 scripts/rehearse_master_demo.py

# Run Phase 13 final release audit (15/15 gates passing)
python3 scripts/verify_phase13_final_release.py
```

---

## 🏗️ 10-Module Architecture & Cloud Infrastructure

```
                                  [ Students: Web / Mobile ]
                                              │ (TLS 1.3 / HTTPS)
                                              ▼
                             [ Nginx / WSGI Gunicorn (4 Workers) ]
                                              │
    ┌─────────────────────────────────────────┼────────────────────────────────────────┐
    ▼                                         ▼                                        ▼
[ Module 1: Student Input ]       [ Module 5: Teaching Harness ]             [ Module 10: Analytics ]
• Multilingual profiles           • 12-State Deterministic Machine           • Bayesian Knowledge Tracing
• Goal & level normalization      • Pydantic state boundary guards           • Bloom mastery radar charts
    │                                         │                                        │
    ▼                                         ▼                                        ▼
[ Module 2: Document RAG ]        [ Module 6: Model Router ]                 [ Dual-Engine Database ]
• PDF / AST formula parsing       • Primary: Gemini 2.5 Flash                • Primary: Neon PostgreSQL
• 1024-D Vector Index             • Secondary: OpenAI GPT-4o                 • Fallback: Persistent SQLite
• Directed Acyclic Concept Graph  • Fallback: Deterministic Harness                    │
    │                                         │                                        ▼
    ▼                                         ▼                              [ Cache Architecture ]
[ Module 3 & 4: Cognition & Plan] [ Module 8 & 9: Multimodal Media ]         • Primary: Upstash Redis
• Concept dependency engine       • SVG Whiteboard / Procedural Math         • Fallback: In-Memory TTL
• Time-budgeted lesson pacing     • 24kHz Neural TTS (ElevenLabs / Local)
• Misconception remediation       • 9-State Avatar (Canvas / D-ID Video)
```

| Module | Primary Cloud Service | Resilient Fallback | Tested Status |
| :--- | :--- | :--- | :--- |
| **Module 1: Student Input** | Local Validation Engine | Strict Pydantic Schema | 100% PASS |
| **Module 2: Document RAG** | Pinecone 1024-D Vectors | Local Dense Cosine + BM25 | 100% PASS |
| **Module 3: Cognitive Model** | Neon PostgreSQL (Pooled) | Persistent Local SQLite | 100% PASS |
| **Module 4: Lesson Planner** | Google Gemini 2.5 Flash | Deterministic Lesson Engine | 100% PASS |
| **Module 5: Teaching Harness**| 12-State Core Orchestrator| Invariant Policy Engine | 100% PASS |
| **Module 6: Model Router** | Gemini 2.5 Flash | OpenAI GPT-4o $\rightarrow$ Harness | 100% PASS |
| **Module 7: Assessment** | Misconception Classifier | Contrastive Rubric Evaluator| 100% PASS |
| **Module 8: Visual Engine** | Dynamic Procedural SVG | MathJax / Matplotlib | 100% PASS |
| **Module 9: Media Engine** | ElevenLabs Neural Speech | 24kHz Studio PCM / Canvas | 100% PASS |
| **Module 10: Analytics** | Upstash Redis REST | Thread-Safe Memory Cache | 100% PASS |

---

## 📚 Essential Documentation Suite

- 📖 [**Final Release Verification & Certification (18/18 PASS)**](docs/FINAL_RELEASE_VERIFICATION.md): Complete audit matrix, automated test metrics (422/422 passing), browser E2E results, and bug remediation report.
- 📖 [**Production Deployment Runbook (17 Topics)**](docs/DEPLOYMENT.md): Comprehensive guide to prerequisites, environment configs, database migrations, Gunicorn WSGI, Docker, and failure recovery.
- 🎤 [**Hackathon Live Demo Script**](docs/HACKATHON_DEMO_SCRIPT.md): Minute-by-minute 3-to-7 minute presentation flow with exact cues and spoken narrative.
- 🎯 [**Demo Talking Points & Rationale**](docs/DEMO_TALKING_POINTS.md): High-impact answers to "Why this exists", "Why RAG + Knowledge Graph", "Why deterministic harness", and "Why personalization".
- 🛡️ [**Live Demo Failure Recovery Plan**](docs/LIVE_DEMO_FAILURE_PLAN.md): Emergency protocols for Wi-Fi drops, API rate limits, and quota exhaustion to guarantee 100% uptime on stage.
- 📊 [**Machine Learning Course Certification**](docs/ML_COURSE_CERTIFICATION.md): Audit of the 5-unit syllabus, formulas, and benchmark metrics.
- 🎓 [**Personalized Student Platform Guide**](docs/STUDENT_PLATFORM.md): Architecture of multi-course, multi-student, exam planning, and doubt vaults.

---

## ⚖️ Transparent Disclosures & Honest Limitations

1. **Third-Party API Quotas**: In live cloud environments without funded API keys, cloud avatar video (D-ID) and neural voice (ElevenLabs) seamlessly degrade to the local procedural canvas avatar and 24kHz local synthesis without error or interruption.
2. **Database Network Partitions**: If the managed cloud PostgreSQL endpoint experiences connection timeouts or DNS resolution issues, the system automatically routes transactions to the local SQLite engine with full data consistency.
3. **AST Sandbox Boundaries**: The Python code execution sandbox intentionally restricts arbitrary standard library access (`os`, `sys`, `socket`, `open`) to prevent remote code execution vulnerabilities; mathematical operations via `math` and standard numeric routines are permitted.

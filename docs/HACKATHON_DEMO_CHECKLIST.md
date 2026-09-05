# 📋 Apurva AI Teacher — Hackathon Demo Checklist

This document provides the canonical step-by-step checklist for judges, reviewers, and presenters executing the Apurva AI Teacher multimodal demonstration.

---

## 🛠️ 1. Pre-Demo Setup & Environment Checks

- [ ] **Python Environment**: Python 3.10+ installed and virtual environment activated (`source .venv/bin/activate`).
- [ ] **Dependencies**: All dependencies installed via `pip install -r requirements.txt`.
- [ ] **Configuration**: `.env` file present and configured from `.env.example`.
- [ ] **Gemini LLM**: `GEMINI_API_KEY` configured and verified as primary model (`gemini-3.5-flash-lite`).
- [ ] **Relational Database**: Neon PostgreSQL connected via `DATABASE_URL` (or auto-fallback to SQLite enabled).
- [ ] **Vector Database**: Pinecone connected with 1024-D Serverless index (`PINECONE_API_KEY`).
- [ ] **Cache & Locks**: Upstash Redis configured via REST TLS endpoint.
- [ ] **Neural Voice**: ElevenLabs TTS API key configured for multilingual Hindi/English audio.
- [ ] **Automated Tests**: Test suite passes with 100% green status (`python3 -m pytest tests/ -v`).
- [ ] **Server Startup**: Application server launched cleanly (`python3 run.py`).
- [ ] **Browser Access**: Canonical demo UI opens at `http://127.0.0.1:5000/demo` (or `http://127.0.0.1:5000/`).

---

## 🚀 2. Live Demo Execution (7-Stage Closed-Loop Workflow)

### Stage 1: Learner Setup & Topic Selection
- [ ] Learner profile initialized (Beginner, 10 minutes time budget).
- [ ] Language set to Hindi (`hi`) or English (`en`).
- [ ] Topic specified: **Ohm's Law** (or click the 1-click **"🚀 Run Ohm's Law Demo"** button).

### Stage 2: Document Ingestion & RAG
- [ ] PDF document uploaded and parsed.
- [ ] Native layout engine extracts sections, tables, formulas.
- [ ] Semantic chunking generates 1024-D vector embeddings.
- [ ] Pinecone index stores and retrieves grounded physics evidence.

### Stage 3: Dynamic AI Lesson Planning
- [ ] Module 4 Lesson Planner generates structured segment outline.
- [ ] Pedagogical strategy selected (`DIRECT_EXPLANATION`).
- [ ] Cognitive time budget allocated across learning objectives.

### Stage 4: Multimodal Classroom & Neural Speech
- [ ] Interactive animated SVG circuit diagram renders on the whiteboard.
- [ ] ElevenLabs generates crisp Hindi neural audio explanation.
- [ ] Synchronized transcript text highlights key concepts ($V = I \times R$).

### Stage 5: Conceptual Checkpoint & Speech STT
- [ ] Formative assessment question generated: *"What happens to current if resistance increases?"*
- [ ] Student submits audio or text response exhibiting common misconception: *"Current will double because resistance pushes electrons."*
- [ ] Local STT / Voice input engine transcribes audio input.

### Stage 6: Misconception Detection & Dynamic Remediation
- [ ] Misconception Engine diagnoses `inverse_relationship_confusion` (Severity: 0.85).
- [ ] Teaching Harness dynamically shifts pedagogical strategy from `DIRECT_EXPLANATION` to `SIMPLE_ANALOGY`.
- [ ] Visual Engine immediately renders the **Hydraulic Water Pipe Constriction** SVG diagram.
- [ ] Adaptive explanation plays explaining resistance as a narrow water pipe bottleneck.
- [ ] Retest question presented; student answers correctly ($I = V/R \rightarrow$ current decreases).
- [ ] Mastery score Bayesian update increases from 0.20 to 0.88.

### Stage 7: Analytics, Bloom Radar & Learning Roadmap
- [ ] Bloom cognitive taxonomy radar chart displays conceptual mastery.
- [ ] Misconception resolution history documented.
- [ ] Gated prerequisite curriculum roadmap highlights unlocked topics (Kirchhoff's Laws).
- [ ] Downloadable learning summary report generated.

---

## 🧠 3. Machine Learning Course & College Student Platform Demonstration

### 1-Click Machine Learning College Course Flow
- [ ] Click the **"🧠 ML College Course"** button in the header bar.
- [ ] Verifies ingestion of authentic 5-unit college curriculum from Chennai Institute of Technology (AD5305 / CS4403).
- [ ] Active unit and concept displayed: **Unit III — Backpropagation & Neural Networks**.
- [ ] Grounded chalkboard SVG visual renders: nodes, layer transitions, and gradient updates.
- [ ] Verified teaching script displayed with citations to Unit III course notes (Page 24).
- [ ] Checkpoint question generated on backpropagation chain rule invariant.
- [ ] Simulated misconception (random weight guessing) immediately diagnosed and remediated with contrastive explanation.
- [ ] Retest submission verifies correct gradient descent update and updates concept mastery to $0.95$.

### Multi-Course Collegiate Learning Platform
- [ ] **Home Dashboard**: View *"What should I study now?"*, upcoming exam countdown, and exam readiness percentage.
- [ ] **My Courses Tab**: Inspect 4 enrolled college courses (Machine Learning, DSA, DBMS, Physics).
- [ ] **Material Library**: Upload and inspect lecture notes with SHA-256 deduplication and source chunk traceability.
- [ ] **Exam Planner Tab**: Inspect dependency-aware 7-day or 30-day study schedule with dynamic replanning.
- [ ] **Assignments Tab**: Generate adaptive assignments and review rubric-evaluated submissions.
- [ ] **Ask Teacher / Doubt Bar**: Type *"Explain that again with an everyday analogy"* $\rightarrow$ Teacher resolves doubt in context.
- [ ] **Video Interruption**: Click *"Ask Doubt"* $\rightarrow$ Lesson pauses at exact timestamp $\rightarrow$ Click *"Resume"* to seamlessly pick up right where paused.
- [ ] **Teaching Controls**: Test *"Explain simpler"*, *"Show visually"*, *"Give hint"*, or switch language to Hindi (`hi`) / Tamil (`ta`).

---

## 🔍 4. Post-Demo & System Verification

- [ ] **Judge Telemetry**: Open the "Judge Telemetry" drawer and verify zero raw secrets or connection strings are shown.
- [ ] **Runtime State**: Confirm session state transitioned cleanly across all teaching states.
- [ ] **Data Isolation**: Confirm Student A cannot access Student B's materials, tasks, or RAG chunks.
- [ ] **Zero Exposed Secrets**: Verify `.env` is gitignored and no API keys are present in version control.
- [ ] **No Errors**: Browser console and server terminal have 0 uncaught exceptions.
- [ ] **Reproducibility**: Entire flow can be repeated dynamically for any student profile or subject.


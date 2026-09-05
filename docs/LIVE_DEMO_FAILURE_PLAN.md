# 🛡️ Apurva AI Teacher — Live Demo Failure Recovery Protocol
## Fail-Safe Emergency Runbook for Hackathon & Live Stage Presentations

In live hackathon environments, conference Wi-Fi fails, cloud APIs experience rate limits, and third-party services suffer unexpected outages. **Apurva AI Teacher** is designed from the ground up to **never crash on stage**.

This document outlines the exact fallback mechanisms and presenter actions to ensure a seamless, professional demonstration regardless of external conditions.

---

## 🚨 Emergency Matrix & Action Plans

### Scenario 1: Wi-Fi Drops or Internet Disconnects Mid-Demo
- **What Happens Automatically**:
  - The model router seamlessly switches from Gemini/OpenAI to the **Deterministic AI Teaching Harness** (`app/harness/orchestrator.py`).
  - Audio switches from ElevenLabs to the **Local 24kHz Studio PCM Engine**.
  - Avatar operates locally using the **Procedural Presenter Engine** (HTML5 Canvas + SVG).
  - Database switches to the local **Persistent SQLite Engine** (`data/ai_teacher.db`).
- **Presenter Action**:
  - Continue speaking without hesitation. Do NOT apologize or reload the browser.
  - The lesson, checkpoint questions, audio, and avatar will continue functioning smoothly.
- **Presenter Talking Point (Turn into a Win)**:
  > *"Notice how the classroom continues without interruption even though the conference Wi-Fi experienced a packet drop. We built Apurva with an autonomous local teaching harness specifically because university students in rural or low-bandwidth areas cannot depend on unbroken gigabit fiber."*

---

### Scenario 2: Google Gemini or OpenAI API Rate Limit (HTTP 429)
- **What Happens Automatically**:
  - The Model Router (`app/router/router.py`) detects the HTTP 429 or timeout.
  - If Gemini fails, it attempts OpenAI GPT-4o.
  - If both cloud LLMs fail or credentials are exhausted, the **Deterministic Teaching Harness** immediately supplies the pre-verified pedagogical response from the course knowledge graph.
- **Presenter Action**:
  - None required; the response latency will actually drop from ~1.5s to <100ms.
- **Presenter Talking Point**:
  > *"Our dual-tier cloud router + deterministic harness architecture prevents catastrophic failure. When commercial LLM APIs throttle or spike in latency, our deterministic pedagogical engine takes over seamlessly."*

---

### Scenario 3: ElevenLabs TTS Quota Exhausted
- **What Happens Automatically**:
  - The Media Engine (`app/media/tts/factory.py`) catches the quota error.
  - Audio generation instantly routes to the local **24kHz Studio Waveform Synthesizer** / native OS speech synthesis.
  - Subtitles and lip-sync timings remain 100% synchronized with the audio duration.
- **Presenter Action**:
  - Continue playback normally.
- **Presenter Talking Point**:
  > *"We utilize high-efficiency local audio synthesis as an instant fallback to ensure zero classroom downtime even if cloud voice quotas are reached."*

---

### Scenario 4: D-ID Video Avatar Credit Exhaustion or Video Stutter
- **What Happens Automatically**:
  - The Avatar Engine (`app/media/avatar/factory.py`) automatically falls back to the **Procedural Canvas Presenter**.
  - Renders 9 expressive pedagogical states, dynamic blinking, natural head tilts, and real-time lip-sync derived from audio amplitudes.
- **Presenter Action**:
  - Highlight the smooth, responsive Canvas avatar on the screen.
- **Presenter Talking Point**:
  > *"Instead of relying exclusively on high-latency video streaming, our procedural avatar renders at 60 FPS directly in the browser with zero bandwidth overhead."*

---

### Scenario 5: Neon PostgreSQL or Upstash Redis Latency / Unreachable
- **What Happens Automatically**:
  - SQLAlchemy session manager intercepts the connection error and points all queries to `data/ai_teacher.db`.
  - Cache manager falls back to thread-safe in-memory Python dictionaries with per-key TTL.
- **Presenter Action**:
  - None required. All student profiles, doubt bookmarks, and course documents remain fully queryable.

---

### Scenario 6: Presenter Accidentally Closes Tab or Browser Crashes
- **What Happens Automatically**:
  - All student states, lesson progress, and doubt bookmarks are persisted in the database.
- **Presenter Action**:
  1. Re-open browser to `http://localhost:5001/` (or `http://localhost:5173/`).
  2. Click on the student profile or course.
  3. The lesson restores to the latest saved timestamp and completed checkpoints.
- **Presenter Talking Point**:
  > *"Because all state transitions are stored in our persistent database, a student can switch devices or refresh their browser and pick up right where they left off."*

---

## 📋 Pre-Demo Verification Checklist (Run 10 Mins Before Stage)

1. **Verify Backend Server Running**:
   ```bash
   curl -f http://localhost:5001/api/v1/health
   # Must return status 200 with JSON payload
   ```
2. **Run Quick 1-Run Rehearsal**:
   ```bash
   python3 scripts/rehearse_master_demo.py
   # Confirms 16/16 steps green in ~2.5 seconds
   ```
3. **Open Browser to Primary Port**:
   Open Chrome / Safari to `http://localhost:5001/` and verify the Dashboard loads with zero console red errors.
4. **Unmute Laptop Audio**:
   Ensure laptop speakers are set to ~75% volume for clear avatar speech playback.

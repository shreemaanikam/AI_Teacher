# 🎤 Apurva AI Teacher — Hackathon Demo Script
## 3-to-7 Minute Master Presentation & Live Judging Flow

This document provides a minute-by-minute live presentation guide for presenting **Apurva AI Teacher** to hackathon judges, academic leadership, and collegiate educators.

---

## ⏱️ Master Timeline Overview

| Timestamp | Phase | Screen / Feature | Key Message / Narrative |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:45** | **The Problem & Value Prop** | Welcome Screen / Persona Selection | Generic chatbots fail university education. Apurva is an autonomous college professor. |
| **0:45 – 1:30** | **Upload-Driven Intelligence** | Dashboard / Course Ingestion | Real university material ingestion (CIT Chennai AD5305 Machine Learning). RAG + Knowledge Graph. |
| **1:30 – 2:45** | **Live Multimodal Classroom** | Classroom Screen / Avatar | Human avatar teaching Gradient Descent with lip-sync, SVG whiteboard, and synchronized audio. |
| **2:45 – 3:45** | **The Breakthrough: Live Interruption** | Classroom / Doubt Bar | Student interrupts mid-lesson. Apurva pauses video, answers doubt contextually, and resumes at exact second. |
| **3:45 – 4:30** | **Adaptive Remediation & Code Lab** | Checkpoint / Practical Lab | Misconception diagnosis, strategy shift, and AST-sandboxed Python code debugging. |
| **4:30 – 5:30** | **Personalization & Exam Readiness** | Exam Planner / Analytics | 5-unit exam schedule, dynamic replanning on missed days, and Bloom taxonomy mastery radar. |
| **5:30 – 6:00** | **Judge Telemetry & Closing** | Telemetry Modal / Q&A | Architectural resilience (dual-engine DB, model router, 399 tests passing). |

---

## 🎬 Minute-by-Minute Step Guide

### **Minute 0:00 – 0:45: The Problem & The Solution**
- **Action**: Open browser to `http://localhost:5001/` (or `http://localhost:5173/`). The Student Dashboard or Onboarding screen is visible.
- **Spoken Narrative**:
  > *"Judges, today millions of college students sit in 60-person lecture halls where professors cannot pause for every question, and at night, students are left alone trying to decipher complex technical syllabi.
  > If they ask ChatGPT or Gemini, they get walls of generic text without syllabus alignment, without memory of their prior tests, and with no pedagogical structure.
  > We built **Apurva AI Teacher** — the world’s first autonomous, upload-driven, multimodal AI college teacher. Apurva doesn't just chat; she teaches, observes misconceptions, executes code labs, builds exam schedules, and lets students interrupt her mid-sentence just like a real professor in office hours."*

---

### **Minute 0:45 – 1:30: Real University Material & Course Ingestion**
- **Action**:
  1. Click **Courses** tab in the sidebar or top navigation.
  2. Select **"AD5305: Machine Learning"** (Chennai Institute of Technology syllabus).
  3. Show the **Course Documents** section displaying uploaded PDFs: Unit 1 to Unit 5.
- **Spoken Narrative**:
  > *"Apurva is completely upload-driven. Here we have ingested the real 5-unit Machine Learning syllabus from Chennai Institute of Technology.
  > Rather than relying on naive text chunking, our RAG pipeline performs AST parsing on formulas, extracts concept dependency Directed Acyclic Graphs (DAGs), and embeds concepts into a 1024-dimensional vector space.
  > Notice that every single claim Apurva makes has 100% source provenance pointing back to authentic university lecture slides."*

---

### **Minute 1:30 – 2:45: Live Classroom & Human Teacher Avatar**
- **Action**:
  1. Click **"Start Learning: Gradient Descent & Learning Rate"**.
  2. The Classroom loads:
     - The **Human AI Teacher Avatar** appears on the left with natural breathing and realistic expressions.
     - The **SVG Whiteboard** renders the loss surface parabola and weight update equations.
     - Studio neural audio plays synchronized with real-time lip movements.
- **Spoken Narrative**:
  > *"Welcome to the classroom. This is not a static video.
  > On the left, our AI Teacher avatar uses a procedural presenter engine with 9 distinct pedagogical emotional states — including explaining, thinking, encouraging, and celebrating.
  > Her lip movements are dynamically computed from audio amplitude envelopes at 24kHz.
  > On the right, the interactive board renders dynamic SVG visuals of the gradient descent loss surface."*

---

### **Minute 2:45 – 3:45: The "Wow" Factor — Live Mid-Lesson Interruption & Exact Resume**
- **Action**:
  1. While the teacher is speaking (around timestamp ~0:45), click the **"✋ Ask Doubt"** button (or press the microphone button).
  2. Observe: The lesson playback **immediately pauses**, the avatar enters the `LISTENING` state, and a bookmark is stored at `0:45.2`.
  3. Type or speak: *"Wait, why did we subtract the gradient instead of adding it?"*
  4. Click **Submit Doubt**.
  5. The teacher avatar switches to `THINKING`, then `EXPLAINING`, and delivers a crystal-clear contextual explanation:
     *"We subtract the gradient because the gradient points in the direction of steepest ascent (increasing loss). To reach the minimum error, we must move in the opposite direction!"*
  6. Click **"Resume Lesson"**.
  7. Notice: The video and audio resume at the **exact interrupted timestamp** without missing a beat!
- **Spoken Narrative**:
  > *"Here is our signature breakthrough: in real life, when you raise your hand, your professor stops.
  > With Apurva, the student interrupted mid-sentence. The video state was snapshotted at 45 seconds. Apurva shifted into listening mode, resolved the student's conceptual doubt using course context, and with one click, resumed the lecture seamlessly. No other educational platform offers this level of fluid conversational continuity."*

---

### **Minute 3:45 – 4:30: Adaptive Checkpoint, Misconceptions & AST Code Sandbox**
- **Action**:
  1. Advance to the checkpoint question: *"What happens if the learning rate $\alpha$ is too large?"*
  2. Select the common misconception answer: *"The model converges faster to the optimal weights."*
  3. Submit answer.
  4. Watch the platform trigger **Module 7 Misconception Remediation**:
     - Diagnoses: `Overshooting and divergence confusion`.
     - The avatar shifts to `ENCOURAGING` and dynamically simplifies the explanation.
     - Automatically serves a follow-up re-test.
  5. Click on **Practical Lab**: Run the Python gradient descent debugging drill.
  6. Click **"Run Code"**: Show that safe numerical math executes instantly, and test typing `import os; os.system('ls')` — show that the secure AST sandbox blocks it immediately with `SecurityViolation: Import of 'os' is strictly forbidden`.
- **Spoken Narrative**:
  > *"When the student picks a common distractor, Apurva doesn't just say 'Wrong'. She identifies the exact cognitive misconception, switches pedagogical strategy to an intuitive analogy, and provides an immediate adaptive recovery drill.
  > And in our practical lab, students write real Python code executed inside a strict AST-sandboxed environment that permits linear algebra while blocking malicious system exploits."*

---

### **Minute 4:30 – 5:30: Personalized Exam Planner & Dynamic Replanning**
- **Action**:
  1. Navigate to **"Exam Planner"**.
  2. Show the countdown to the University Semester Exam (e.g., 14 days).
  3. Show the day-by-day scheduled study units (Unit 1 to Unit 5).
  4. Click **"Mark Yesterday Missed"** $\rightarrow$ **"Replan Schedule"**.
  5. Watch the planner recalculate the daily workload dynamically based on topic weightage and student mastery velocity.
- **Spoken Narrative**:
  > *"Every college student faces exam stress. Apurva's Exam Planner doesn't give a generic calendar. It calculates student mastery, weighs difficult topics, and plans daily study sessions.
  > If life happens and the student misses a day, Apurva dynamically replans the remaining schedule so the student stays on track for their university finals."*

---

### **Minute 5:30 – 6:00: Telemetry, Architectural Resilience & Wrap-up**
- **Action**:
  1. Click **"Judge Telemetry"** in the top navigation or footer.
  2. Show the real-time component health grid:
     - 399 automated tests passing.
     - Dual database resilience (Neon PostgreSQL + SQLite fallback).
     - Dual LLM router (Gemini 2.5 Flash + OpenAI fallback + Deterministic Harness).
     - Multilingual support verified (English, Hindi, Tamil).
- **Spoken Narrative**:
  > *"Under the hood, Apurva is built with collegiate-grade resilience: 399 passing tests, zero secret leakage, dual-engine databases, and a deterministic teaching harness.
  > Apurva gives every college student the experience of a dedicated, world-class professor in their pocket 24/7. Thank you, and we welcome your questions!"*

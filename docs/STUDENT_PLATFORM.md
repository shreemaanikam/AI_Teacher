# 🎓 Apurva AI Teacher — Personalized College Student Platform (Phase 9)

## Executive Summary

The **Personalized College Student Platform** elevates Apurva AI from a fixed concept demonstrator into an **autonomous, upload-driven, multi-course college AI educator**. Centered entirely around the collegiate learner, the platform dynamically ingests authentic university course materials (lecture notes, syllabi, problem sheets), builds concept dependency graphs, computes principled study schedules for upcoming exams, provides adaptive homework with rubric evaluation, solves multi-turn student doubts with contextual memory, supports live video interruption and resumption, and executes pedagogical teaching controls.

---

## 🏛️ Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PERSONALIZED STUDENT LEARNING HOME                     │
│  - "What should I study now?" Dynamic Recommendation                         │
│  - Upcoming Exam Countdown & Principled Readiness Percentage (0-100%)       │
│  - Today's Personalized Study Blocks & Task Deadlines                       │
└───────────────────────┬───────────────────────────────┬─────────────────────┘
                        │                               │
       ┌────────────────▼────────────────┐     ┌────────▼────────────────┐
       │   MULTI-COURSE MATERIAL ENGINE  │     │   EXAM STUDY PLANNER    │
       │  - Multi-Format Uploads         │     │  - Dependency-Aware     │
       │  - SHA256 Deduplication         │     │  - Weak Area Priority   │
       │  - Source Chunk Traceability    │     │  - Dynamic Replanning   │
       └────────────────┬────────────────┘     └────────┬────────────────┘
                        │                               │
       ┌────────────────▼───────────────────────────────▼────────────────┐
       │               ADAPTIVE MULTIMODAL CLASSROOM                     │
       │  - Realistic Human AI Teacher Avatar & Voice                    │
       │  - Dynamic Visual Chalkboard (Deterministic SVGs & Formulas)    │
       │  - Live Video Interruption & Exact-Timestamp Resume             │
       │  - Multi-Turn Contextual Doubt Vault ("Explain that again")     │
       │  - Personalized Teaching Controls (Simpler, Visual, Hint, Hindi)│
       └────────────────┬───────────────────────────────┬────────────────┘
                        │                               │
       ┌────────────────▼────────────────┐     ┌────────▼────────────────┐
       │    ADAPTIVE HOMEWORK & RUBRIC   │     │    LEARNING ANALYTICS   │
       │  - Conceptual & Numerical Drill │     │  - Cross-Course Graph   │
       │  - Subject Practical Tasks (ML) │     │  - Mastery Trajectory   │
       │  - Rubric-Scored Evaluations    │     │  - Formal Mentor Report │
       └─────────────────────────────────┘     └─────────────────────────┘
```

---

## 👤 1. Student Identity & Multi-Course Profile (Phases 9A & 9B)

Every student maintains a persistent academic profile containing:
- **Collegiate Metadata**: Institution (e.g., IIT Bombay, NIT Trichy, CIT Chennai), Department, Degree (B.Tech / B.E. / M.Tech), Year (1–4), Semester (1–8).
- **Study Budget & Goals**: Target GPA / Exam score (e.g., 90%, 98%), Daily available study hours (e.g., 2.0 to 4.5 hours/day).
- **Cognitive Preferences**: Learning style (`VISUAL_AND_ANALOGIES`, `FIRST_PRINCIPLES`, `STEP_BY_STEP`), Preferred language (`en`, `hi`, `ta`).
- **Enrolled Courses**: Multiple simultaneous subjects:
  - Machine Learning (AD5305 / CS4403)
  - Data Structures & Algorithms (CS201)
  - Database Management Systems (CS301)
  - Operating Systems (CS304)
  - Physics & Circuit Theory (PH101)

---

## 📁 2. Upload Pipeline & Material Library (Phases 9C, 9D, 9E, 9F)

- **Supported Formats**: PDF lecture slides, handwritten notes, Word documents, text files, and direct syllabus topic synthesis.
- **6-Stage Pipeline**: `UPLOAD` $\rightarrow$ `PARSE` $\rightarrow$ `UNDERSTAND` $\rightarrow$ `STRUCTURE` $\rightarrow$ `INDEX` $\rightarrow$ `READY`.
- **Deduplication**: SHA-256 checksums prevent redundant re-processing of identical documents.
- **Strict Provenance**: Every major concept, formula, and algorithm links back to document name, page number, and chunk ID. Never fabricates source references.

---

## 📊 3. Student Home Dashboard & Personalized Next Action (Phases 9H, 9V)

The home dashboard answers five critical student questions immediately:
1. **"What should I study now?"**: Princpled priority based on exam proximity ($t \le 7$ days) and detected concept weakness ($mastery < 0.60$).
2. **"When is my next exam?"**: Live countdown across all enrolled subjects.
3. **"How prepared am I?"**: Principled readiness percentage calculated from syllabus coverage, average concept mastery, and open misconceptions.
4. **"What tasks are due today?"**: Today's 20-30 minute focused study blocks and homework deadlines.
5. **"What are my weak concepts?"**: High-priority topics requiring targeted remediation.

---

## 🗓️ 4. Dependency-Aware Exam Planner & Dynamic Replanning (Phases 9J, 9K)

- **Multi-Day Schedule Generator**: Allocates daily study blocks between current date and target exam date:
  - **Early Days**: Progressive unit conceptual foundations.
  - **Penultimate Days ($t-2$)**: High-priority weak area reinforcement and misconception remediation.
  - **Pre-Exam Day ($t-1$)**: Timed full mock assessments and practical problem-solving.
  - **Exam Day ($t$)**: Rapid formula summaries, invariants, and exam strategy tips.
- **Dynamic Replanning**: Triggered when a student misses study days, changes available hours, shifts exam dates, or exhibits newly diagnosed misconceptions. Recalculates remaining days without blind task appending.

---

## 📝 5. Adaptive Assignments & Subject Practical Learning (Phases 9M, 9N, 9O)

- **Assignment Generator**: Creates tailored practice sets containing MCQs, conceptual derivations, and numerical problems adapted to student mastery.
- **Rubric-Scored Evaluation**: Grades student submissions against multi-criteria rubrics, detects lingering misconceptions, and updates Bayesian concept mastery snapshots.
- **Subject-Specific Practical Tasks**:
  - **Machine Learning**: Python implementations (Batch gradient descent update step $w_{new} = w - \eta \nabla L$, classification confusion metrics, K-Means centroid recomputation).
  - **DBMS**: SQL grouping and aggregation queries (`JOIN`, `GROUP BY`, `HAVING`).
  - **Data Structures**: Binary search tree in-order traversal, Floyd's cycle detection.
  - **Physics**: Equivalent circuit resistance calculations and Ohm's Law current analysis ($I = V / R_{eq}$).

---

## 🙋‍♀️ 6. Ask Teacher, Contextual Memory & Live Interruption (Phases 9P, 9Q, 9R)

- **Ask Teacher**: First-class capability accessible via text, voice, or quick chips.
- **Contextual Memory**: Understands colloquial follow-ups without restating context:
  - *"Can you explain that again?"* $\rightarrow$ Detects active concept, formulates simpler analogy.
  - *"Why was that negative?"* $\rightarrow$ Resolves negative gradient descent update direction or entropy formula signs.
  - *"What is the formula?"* $\rightarrow$ Provides canonical latex formula and grounded parameter definitions.
- **Doubt Vault**: Records all doubts with status (`UNRESOLVED`, `RESOLVED`, `BOOKMARKED`, `MASTERED`).
- **Video Interruption & Seamless Resume**:
  - Student clicks "Ask Doubt" during video lesson $\rightarrow$ Teaching state pauses, exact timestamp saved (e.g., $74.5$s).
  - Teacher immediately resolves doubt with empathetic avatar cues.
  - Student clicks "Resume" $\rightarrow$ Video and lesson seamlessly resume at $74.5$s with natural transitional continuation prompt.

---

## 🎛️ 7. Personalized Teaching Controls (Phase 9S)

Real backend pedagogical controls wired to live teaching logic:
- **Explain Simpler**: Employs everyday intuitive analogies (e.g., hill-climbing in fog, book categorization).
- **Another Example**: Generates concrete industry applications (e.g., Spotify recommendation, autonomous vehicle braking).
- **Show Visually**: Dynamically renders dedicated vector chalkboard SVGs.
- **Give a Hint**: Scaffolds reasoning around invariants without revealing the solution.
- **Slow Down**: Breaks explanations into 3 paced, sequential micro-steps.
- **Repeat**: Re-emphasizes central mathematical invariance.
- **Practice This**: Serves an immediate single-question check for understanding.
- **Switch Language**: Localizes instruction into Hindi (`hi`) or Tamil (`ta`) while strictly preserving formulas and variables.

---

## 🌐 8. Cross-Course Knowledge Graph & Academic Mentor Reports (Phases 9K, 9L, 9N)

- **Cross-Subject Knowledge Graph**: Identifies conceptual inter-dependencies across college courses:
  - Linear Algebra & Matrices $\rightarrow$ PCA & Dimensionality Reduction (ML)
  - Multivariable Calculus $\rightarrow$ Gradient Descent & Optimization (ML)
  - Balanced Binary Search Trees $\rightarrow$ B-Tree & B+ Tree Indexing (DBMS)
  - Graph Traversals $\rightarrow$ Deadlock Detection & Banker's Algorithm (OS)
  - Relational Calculus $\rightarrow$ Query Optimization (DBMS)
- **Academic Mentor Report**: Generates formal collegiate progress reports for faculty mentors, academic advisors, and parents, summarizing mastery trajectory, exam readiness, strengths, and recommended focus areas.

---

## 👥 9. Multi-Student Personalization Verification (Phase 9Y)

| Dimension | Student A (Aarav Gupta) | Student B (Bhavya Nair) | Verification Result |
| :--- | :--- | :--- | :--- |
| **Collegiate Standing** | NIT Delhi • Year 2 • CSE | BITS Pilani • Year 3 • CSE | Distinct Profiles Verified ✅ |
| **Available Study Time** | 2.0 Hours / Day | 4.5 Hours / Day | Budget-Aware Scheduling ✅ |
| **Exam Horizon** | Urgent (7 Days) | Extended (30 Days) | Dynamic Horizon Scaling ✅ |
| **Weak Knowledge Area** | Unit 3: Neural Networks ($0.35$) | None ($0.95$ Unit 1 Mastery) | Targeted Remediation Prioritized ✅ |
| **Next Action Recommendation** | Focus revision on Unit 3 Backprop | Advance to Unit 4 Unsupervised Learning | Meaningfully Distinct Behaviors ✅ |
| **Language Preference** | Hindi (`hi`) Bilingual | English (`en`) Technical | Localized Avatar Script Delivery ✅ |

---

## 🔒 10. Data Isolation & Security (Phases 9Z & 9AK)

- **Multi-Tenant Data Isolation**: Verified across student boundaries (profiles, uploaded documents, document chunks, study tasks, exam plans, practical submissions, media files). Zero cross-student data leakage.
- **Zero Exposed Secrets**:
  - No API keys in telemetry or frontend bundles.
  - `.env` strictly gitignored and excluded from version control.
  - Clean `.env.example` template provided.
- **Autonomous Fallbacks**: Seamless zero-crash fallbacks for LLMs, databases (Neon $\rightarrow$ SQLite), vector databases, TTS, and avatars.

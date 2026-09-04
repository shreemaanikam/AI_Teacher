# Project Requirements Document

## Document control

- Product: **AI Teacher**
- Source brief: `../../technical_assessment_document.md`
- Status: approved design baseline; implementation has not started
- Last updated: 2026-08-31

This document defines product intent and acceptance. `../execution/features.md` records implementation status; planned behavior must not be represented as complete.

## Product vision

AI Teacher turns a topic or uploaded educational source into a personalized, multilingual, video-led lesson that teaches in a human-like loop:

```text
Understand learner -> Plan -> Explain -> Demonstrate -> Question
        ^                                             |
        |                                             v
 Recommend next <- Record mastery <- Adapt <- Evaluate
```

Unlike a question-answer chatbot, it controls lesson sequencing, grounds material-derived claims in sources, pauses for interaction, diagnoses misconceptions, changes its explanation, and verifies understanding before progressing.

The teaching intelligence is a **controlled multi-agent engine**. A Master Teaching Orchestrator delegates bounded work to specialist agents for source curation, learner modeling, curriculum, lesson planning, explanations, examples, quizzes, response analysis, adaptation, fact-checking, voice, visuals, avatar production, composition, accessibility, and reporting. Agents exchange versioned artifacts through the orchestrator; they do not form an uncontrolled peer-to-peer conversation.

## Users and goals

- Students from school through professional level, including exam/interview learners.
- Multilingual learners whose teaching language differs from the source.
- Educators or reviewers inspecting plans and reports.

Success means: material-derived claims are cited; profile and time change the plan; lessons contain checkpoints; wrong answers trigger a different strategy and re-check; avatar, voice, captions, and visuals form one timeline; progress informs future recommendations.

## Scope

### MVP / mandatory

- Account and learner profile.
- Topic-based teaching without an upload.
- PDF, DOCX, PPTX, and TXT ingestion; optional OCR for scanned PDFs.
- Chapter/section selection, parsing, chunking, embedding, retrieval, and citations.
- Time-budgeted lesson plans and multi-day learning paths.
- Beginner, intermediate, and advanced depth.
- English, Hindi, and Hinglish with mid-lesson switching; extensible locales.
- Script, voice, avatar, captions, and subject-aware visuals.
- Interactive MCQ, conceptual, short-answer, and problem checkpoints.
- Evaluation, misconception detection, remediation, re-check, final quiz, report, mastery, and next steps.
- Asynchronous progress and recoverable ingestion/media failures.

### Later enhancements

- Real-time streaming avatar, emotion awareness, personalities, flashcards, homework, exam/revision modes, concept maps, advanced analytics, simulations, classrooms, mobile apps, and optional local-model deployment.

### Non-goals for MVP

- Replacing accredited teachers or issuing qualifications.
- Safety-critical professional certification.
- Arbitrary web browsing as an uncited knowledge source.
- DRM bypass or redistribution of uploaded works.
- Mandatory photorealistic long-form video; an interactive composed timeline is acceptable.

## Functional requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-001 | Register, sign in/out, and access only owned resources. | Must |
| FR-002 | Store level, goals, known topics, style, language, accessibility preferences, and time budget. | Must |
| FR-003 | Use prior mastery and history in future planning. | Must |
| FR-010 | Upload PDF, DOCX, PPTX, or TXT within configured limits and see processing state. | Must |
| FR-011 | Extract structure, page/slide positions, language, metadata, and OCR image-only pages when enabled. | Must |
| FR-012 | Normalize, structurally chunk, embed, index, and owner-isolate content. | Must |
| FR-013 | Select a document, chapter, section, or topic as scope. | Must |
| FR-014 | Retain page/slide/section citations and declare low evidence. | Must |
| FR-015 | Retry failed ingestion without duplicate records. | Must |
| FR-020 | Accept source/topic, objective, level, language, time, depth, and style. | Must |
| FR-021 | Plan ordered objectives, prerequisites, timings, examples, visuals, checkpoints, and assessment coverage. | Must |
| FR-022 | Fit time by changing breadth/depth, not merely shortening prose. | Must |
| FR-023 | Run explain-demonstrate-question-evaluate-adapt while preserving context. | Must |
| FR-024 | Pause, resume, replay, seek completed segments, ask follow-ups, and switch language. | Must |
| FR-025 | Answer follow-ups within lesson scope and return to planned state. | Must |
| FR-026 | Produce prerequisite-aware multi-session paths for broad topics. | Should |
| FR-030 | Give every segment narration, timed captions, avatar output, and a visual scene. | Must |
| FR-031 | Select subject-aware equations/graphs, diagrams, timelines/maps, code flows, or illustrations. | Must |
| FR-032 | Generate/cached media asynchronously and assemble a synchronized timeline. | Must |
| FR-033 | Fall back to usable voice/captions/visuals when avatar generation fails. | Must |
| FR-040 | Support MCQ, short answer, teach-back, and numeric/problem responses. | Must |
| FR-041 | Return correctness, confidence, rubric evidence, misconception, feedback, and action. | Must |
| FR-042 | Remediate with a changed strategy and a new check. | Must |
| FR-043 | Produce final score, strengths, gaps, revision, and next topic. | Must |
| FR-044 | Update concept mastery using recency, difficulty, correctness, hints, and confidence. | Must |
| FR-045 | Show history, reports, citations, and recommendations. | Must |
| FR-050 | Expose queued, processing, ready, failed, and cancelled job states. | Must |
| FR-051 | Permit privacy-conscious operational inspection of failures and local runtime/model health. | Should |
| FR-052 | Treat uploaded instructions as untrusted and unable to override policy. | Must |
| FR-053 | Delete documents and account data subject to retention policy. | Must |
| FR-060 | Coordinate teaching through a master orchestrator and independently replaceable specialist agents with explicit responsibilities. | Must |
| FR-061 | Route all inter-agent work through versioned task/result contracts with traceable inputs, evidence, confidence, and provenance. | Must |
| FR-062 | Prevent agents from directly accessing databases, credentials, or unrestricted learner history; authorized services provide minimum necessary context and validate proposed writes. | Must |
| FR-063 | Persist observable learner evidence separately from AI-inferred traits, including confidence, supporting evidence, model version, expiry/review status, and learner correction/deletion controls. | Must |
| FR-064 | Continue or degrade safely when an optional specialist fails; mandatory artifact failures must be retryable and visible. | Must |
| FR-065 | Permit an agent implementation to run in-process, as a queue worker, or behind an authenticated API without changing its domain contract. | Should |
| FR-070 | Route LLM, embedding, reranking, evaluation, translation, image, speech, and avatar capabilities through replaceable provider interfaces. | Must |
| FR-071 | Select models by capability and quality policy without exposing provider-specific identifiers to domain workflows. | Must |
| FR-072 | Disclose significant third-party APIs, models, libraries, services, licenses, data boundaries, and limitations. | Must |
| FR-073 | Validate probabilistic output with schemas, evidence rules, safety checks, and deterministic teaching policy before it changes state. | Must |
| FR-074 | Track provider/model version, prompt version, evidence, latency, usage, cost, and fallback for each material AI decision. | Must |
| FR-075 | Use provider-backed multilingual STT, TTS, image generation, and avatar/video behind adapters, with typed-input and accessible media fallbacks. | Must |
| FR-076 | Generate short media segments and use FFmpeg plus object storage to normalize, caption, assemble, and deliver adaptive lessons. | Must |

## Non-functional requirements

| ID | Area | Requirement |
| --- | --- | --- |
| NFR-001 | Availability | Production core API target 99.5% monthly; degrade gracefully. |
| NFR-002 | Performance | p95 ordinary API under 500 ms; topic plan under 30 s; uploads/media asynchronous. |
| NFR-003 | Scale | Stateless API scales horizontally; queues absorb AI/media bursts. |
| NFR-004 | Security | TLS, Argon2id, least privilege, signed URLs, tenant filters, validation, rate limits, and CSRF. |
| NFR-005 | Privacy | Minimize personal data; do not log secrets, source text, or full answers by default. |
| NFR-006 | Accessibility | WCAG 2.2 AA target, keyboard control, captions/transcript, reduced motion, and non-video fallback. |
| NFR-007 | Reliability | Idempotent jobs, bounded retry, timeout, cancellation, telemetry, and dead-lettering. |
| NFR-008 | AI quality | Schema-validate LLM output; grounding, moderation, and deterministic rules gate it. |
| NFR-009 | Portability | LLM, speech, avatar, vector, and object storage are behind interfaces. |
| NFR-010 | Cost | Per-user quotas, token/media budgets, caching, and cost telemetry. |
| NFR-011 | Localization | UTF-8 and BCP 47 tags; mixed scripts and text expansion supported. |
| NFR-012 | Auditability | Record prompt, provider/model version, citations, rubric, usage/cost, fallback, and trace IDs. |
| NFR-013 | Agent governance | Every invocation has a purpose-scoped context, deadline, budget, idempotency key, contract version, trace, and terminal outcome. |
| NFR-014 | Modularity | Agent contracts are independent of LLM/provider/deployment mechanism and have conformance tests. |
| NFR-015 | Provider privacy | External services receive only purpose-minimized data under disclosed consent, retention, deletion, and residency controls. |
| NFR-016 | Provider portability | Capability contracts and conformance tests permit provider replacement without changing lesson-domain behavior. |

## Business rules

- Requested time reserves explicit interaction and assessment time.
- Correct/high-confidence responses advance; misconceptions remediate; low evaluator confidence asks clarification.
- Plans may cite only the selected source set within the learner's ownership boundary.
- Questions map to objectives and do not reveal their answers in adjacent visible content.
- Mastery is mutable evidence, not a permanent label.
- Language switching preserves objectives, sources, position, and progress.
- Completion requires a terminal session and report; abandonment remains resumable.
- Only the orchestrator may authorize workflow transitions. Specialist agents propose artifacts or actions; application policy validates them.
- An agent may not invoke another specialist directly. It returns its result to the orchestrator, which decides the next task.
- Learner facts such as attempts remain immutable evidence. Inferences such as “may misunderstand resistance” are confidence-scored, reviewable, and never treated as sensitive diagnoses.
- Provider responses are proposals, not commands; validated application policy owns transitions and persisted cognitive updates.
- Exact technical visuals use deterministic renderers; generative providers are used when illustration is appropriate.

## Acceptance scenarios

1. A beginner uploads an English physics PDF and requests Chapter 4 in Hindi for 20 minutes. The system produces a cited video lesson, detects a wrong answer, changes explanation, re-checks, quizzes, and stores a report.
2. “React interview preparation” works without an upload, uses code visuals, asks questions, answers a follow-up, and resumes the plan.
3. Hindi-to-English switching retains position and assessment context.
4. An image-only PDF is processed through OCR or rejected with a recoverable explanation.
5. Voice/avatar/media provider failure preserves a typed, captioned, visual lesson and offers retry.
6. Identifier tampering cannot expose another user's source, lesson, citation, report, or asset.
7. Replacing a quiz or voice agent implementation leaves orchestrator contracts and stored lesson/session semantics unchanged.
8. A trace shows which agents produced, validated, rejected, or revised every lesson artifact without exposing private prompt content in ordinary logs.
9. Replacing an LLM, embedding, speech, or avatar provider leaves domain contracts and stored session semantics unchanged.
10. A provider outage, timeout, invalid response, or rate limit produces a controlled fallback or visible recoverable state without an illegal teaching transition.

## Constraints and assumptions

- The repository contains documentation only as of 2026-08-31; every feature is `PLANNED`.
- Initial delivery is a responsive web application.
- Probabilistic AI requires grounding, validation, fallbacks, and visible uncertainty.
- Hosted AI/media providers are permitted only behind approved adapters. Provider identity, model/version, licenses/terms, data handling, limitations, and costs must be disclosed.
- Users must have rights to process their uploads.

Requirement-to-feature mapping is in `../execution/features.md`; technical controls are in `../technical/technical_requirement_document.md`; end-to-end paths are in `app_flow.md`.

# Feature Register

## Status

This is the implementation-status source of truth. As of 2026-08-31 the repository contains documentation only; all features are `PLANNED`, no checkboxes are complete, and implementation paths are targets rather than existing files.

Status values: `PLANNED`, `IN_PROGRESS`, `COMPLETE`, `BLOCKED`, `DEPRECATED`, `REMOVED`. A feature becomes `COMPLETE` only after acceptance tests and documentation match working code.

## Index and traceability

| ID | Feature | Status | Requirements | Verification focus |
| --- | --- | --- | --- | --- |
| F-001 | Identity and learner profile | PLANNED | FR-001–003 | Auth, ownership, personalization |
| F-002 | Document ingestion | PLANNED | FR-010–015 | Formats, OCR, retry, isolation |
| F-003 | RAG and citations | PLANNED | FR-012–014 | Retrieval and faithfulness evals |
| F-004 | Topic/material lesson planner | PLANNED | FR-020–022,026 | Level/time/source plan validation |
| F-005 | Subject-aware media lesson | PLANNED | FR-030–033 | Sync, visuals, avatar fallback |
| F-006 | Adaptive teaching runtime | PLANNED | FR-023–025,040–042 | State-machine E2E and concurrency |
| F-007 | Assessment and feedback | PLANNED | FR-040–045 | Rubrics, report, mastery |
| F-008 | Multilingual teaching | PLANNED | FR-002,020,024,030 | Hindi/English/Hinglish continuity |
| F-009 | Learning paths and recommendations | PLANNED | FR-003,026,044–045 | Prerequisites and recommendation rules |
| F-010 | Async jobs and realtime progress | IN_PROGRESS | FR-015,032,050 | Idempotency, retry, reconnection |
| F-011 | Safety, privacy, and operations | PLANNED | FR-051–053 | Upload/prompt safety, deletion, audit |
| F-012 | Multi-agent teaching engine | PLANNED | FR-060–065 | Contracts, orchestration, artifacts, isolation |
| F-013 | Local llama.cpp model platform | PLANNED | FR-070–076 | GGUF registry, CUDA/Vulkan/CPU, supply chain |

## Feature acceptance

### F-001 — Identity and learner profile

- [ ] Register/login/logout and secure session handling.
- [ ] Edit level, goals, prior knowledge, style, language, time, depth, accessibility.
- [ ] Every owned-resource API rejects cross-user access.
- Target areas: `app/api/auth`, `app/services/profile`, `frontend/src/features/auth|profile`.

### F-002 — Document ingestion

- [ ] Signed upload and progress for PDF/DOCX/PPTX/TXT.
- [ ] MIME/size/page validation, malware scan, parsing, optional OCR.
- [ ] Section/page/slide provenance and language detection.
- [ ] Idempotent retry and deletion of source plus derived artifacts.
- Target areas: `app/ingestion`, `app/workers/ingestion`, document UI.

### F-003 — RAG and citations

- [ ] Structure-aware chunks and versioned embeddings.
- [ ] Owner-filtered hybrid retrieval, adjacency expansion, reranking, deduplication.
- [ ] Citation navigation to source location and visible uncertainty.
- [ ] Evaluation dataset meets agreed retrieval and faithfulness thresholds.
- Depends on F-002.

### F-004 — Topic/material lesson planner

- [ ] Request captures topic/source/scope/objective/level/language/time/depth/style.
- [ ] Schema-valid plan maps objectives to evidence, scenes, checkpoints, and assessment.
- [ ] Duration and breadth vary meaningfully for 5, 20, and 60 minute requests.
- [ ] Broad topics optionally produce a prerequisite-aware path.
- Depends on F-001 and F-003 for personalized/material mode.

### F-005 — Subject-aware media lesson

- [ ] Runtime-neutral scene specs render exact equations/graphs/code/timelines/diagrams.
- [ ] Natural TTS, captions, avatar, and visuals synchronize into a timeline.
- [ ] Audio/caption/visual fallback remains playable after avatar failure.
- [ ] Media metadata, cost, cache key, provenance, and accessibility text persist.
- Depends on F-004 and F-010.

### F-006 — Adaptive teaching runtime

- [ ] The documented state machine controls play, pause, question, evaluation, remediation, re-check, and completion.
- [ ] Follow-up answers preserve and return to lesson context.
- [ ] A misconception changes strategy and uses a new question.
- [ ] Duplicate or concurrent submissions cannot advance twice.
- Depends on F-004, F-005, F-007, F-010.

### F-007 — Assessment and feedback

- [ ] Deterministic and rubric graders produce structured feedback/confidence.
- [ ] Low-confidence grading asks clarification and does not alter mastery.
- [ ] Final report lists score, strengths, gaps, revision, and next step.
- [ ] Append-only attempts update rebuildable concept mastery.

### F-008 — Multilingual teaching

- [ ] English, Hindi, and Hinglish planning, voice, captions, questions, evaluation, and remediation.
- [ ] Mid-session switch preserves objective, citations, position, and responses.
- [ ] Mixed-script UI, fonts, wrapping, and screen readers are verified.

### F-009 — Learning paths and recommendations

- [ ] Generate ordered milestones and prerequisites for a broad goal.
- [ ] Update item status from session evidence.
- [ ] Recommend weak prerequisites, unmet objectives, and spaced review with reasons.

### F-010 — Async jobs and realtime progress

- [x] Optional Agora Web RTC adapter joins/leaves, publishes local media, subscribes to remote media, and cleans up tracks.
- [x] Validated Flask credential-bootstrap endpoint exists behind an Agora provider port; development temporary-token mode is documented.
- [ ] Production AccessToken2 minting, authenticated lesson/channel authorization, token renewal, consent, and privacy/residency review.
- [ ] Separate ingestion, AI, and media queues with progress events.
- [ ] Stable idempotency, bounded retry, timeout, cancellation, heartbeat, and dead-letter behavior.
- [ ] SSE reconnects from cursor and reconciles with REST.

### F-011 — Safety, privacy, and operations

- [ ] Upload injection cannot override system policy; unsafe output is moderated/sanitized.
- [ ] Logs redact content/secrets and preserve useful traces/costs.
- [ ] User deletion revokes access then deletes retained data/artifacts.
- [ ] Admin view exposes failure/health/usage metadata without unnecessary private content.

### F-012 — Multi-agent teaching engine

- [ ] Master Teaching Orchestrator runs a versioned, bounded workflow and is the only authority for agent routing and teaching-state transitions.
- [ ] Registry defines each specialist's type/version, contracts, capabilities, timeout, privacy scope, and enabled/canary status.
- [ ] Knowledge, pedagogy, interaction, and media specialists implement the common typed agent port.
- [ ] Agents exchange only versioned task/result envelopes through the orchestrator; direct peer calls fail architecture tests.
- [ ] Purpose-scoped context broker prevents arbitrary database/history access and agents cannot persist domain state.
- [ ] Candidate artifacts pass schema, evidence, safety, ownership, and domain validation before an authorized service accepts them.
- [ ] Workflow budgets bound hops, attempts, deadline, tokens, and cost; cancellation and fallbacks are tested.
- [ ] Agent runs/artifacts expose complete redacted provenance and metrics without chain-of-thought or private content leakage.
- [ ] Learner observations and inferences are separated; active inferences are evidence-backed, confidence-scored, reviewable, expiring, correctable, and deletable.
- [ ] At least one specialist can move between in-process, worker, and fake/remote adapter without changing domain callers.

F-012 is foundational: F-003–F-010 use specialist contracts coordinated by it. This does not imply every specialist is an LLM or separately deployed service.

### F-013 — Local llama.cpp model platform

- [ ] Pinned, checksum-verified `llama.cpp` CUDA, Vulkan, and CPU runtime artifacts start through one Model Runtime Gateway.
- [ ] Hardware discovery selects only tested profiles and reports device, backend, memory, compatible models, and expected performance.
- [ ] NVIDIA CUDA and targeted Intel Vulkan acceptance suites pass; unsupported acceleration falls back locally to CPU or a smaller approved GGUF.
- [ ] Model manager supports explicit allowlisted Hugging Face downloads and verified offline import without arbitrary URLs or partial activation.
- [ ] Manifests retain immutable revision, hash, license, GGUF metadata, quantization, compatibility, memory estimate, evaluations, and status.
- [ ] Agents route by capability profile and share resident `llama-server` instances; no hosted inference path or duplicate per-agent weight loading exists.
- [ ] Fully provisioned teaching works with inference-worker network egress blocked.
- [ ] Reproducible local fine-tuning records dataset/base lineage, licenses/consents, recipe, evaluations, GGUF conversion/quantization, model card, and checksum.
- [ ] Neural voice/avatar/visual models pass the same `llama.cpp` compatibility gate; unsupported architectures use deterministic local tooling or documented degraded mode.
- [ ] Cross-backend evaluation confirms contract equivalence and accepted pedagogy/language quality tolerances.

## Release acceptance

The MVP is demo-ready only when F-001 through F-008, F-010, F-012, F-013, and the mandatory controls in F-011 are complete; F-009 may ship with basic recommendations. The demo must show upload/topic -> multi-agent plan -> grounded media teaching -> response analysis -> adaptation -> final assessment -> report, plus an agent trace and proof that inference remains local on a validated backend.

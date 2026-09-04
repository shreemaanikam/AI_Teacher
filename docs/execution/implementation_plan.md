# Implementation Plan

## Planning rules

This plan orders the target architecture into demonstrable increments. Status is accurate as of 2026-08-31: no implementation task has started. Each task must update `features.md`, tests, schema/architecture when changed, decisions for major choices, and this plan.

## Phases

| Phase | Objective | Tasks | Exit condition |
| --- | --- | --- | --- |
| 0 | Repository, agent, and provider foundation | IP-001–003, IP-017, IP-021 | App boots; contracts/orchestrator/gateway and CI pass |
| 1 | Secure learner/source foundation | IP-004–006 | Owned profile and ready, cited document corpus |
| 2 | Teaching intelligence | IP-007–009 | Valid personalized plan and adaptive text lesson |
| 3 | Video experience | IP-010–011 | Synchronized media timeline with fallback |
| 4 | Outcomes and continuity | IP-012–013 | Report, mastery, paths/recommendations persist |
| 5 | Hardening and demo | IP-014–016 | Quality gates pass and end-to-end demo is repeatable |

## Tasks

| ID | Status | Deliverable | Depends on |
| --- | --- | --- | --- |
| IP-001 | PLANNED | Scaffold FastAPI/Pydantic API, Next.js/React/TypeScript/Tailwind client, configuration, containers, and health endpoints | — |
| IP-002 | PLANNED | PostgreSQL/pgvector models, Alembic, repositories, Redis/Celery, S3 adapter, transactional outbox | IP-001 |
| IP-003 | PLANNED | CI quality gates, structured logging, OpenTelemetry, test fixtures, local-runtime/model fakes | IP-001 |
| IP-004 | PLANNED | Identity, secure sessions, CSRF/rate limiting, ownership policy, learner profile UI/API | IP-002 |
| IP-005 | PLANNED | Signed uploads, validation/scanning, parsers/OCR, section/chunk persistence, progress events | IP-002–004 |
| IP-006 | PLANNED | Embedding, hybrid retrieval/rerank, evidence contract, citation UI and RAG eval corpus | IP-005 |
| IP-007 | PLANNED | Versioned prompt registry, AI Gateway/model router, structured plan schema, time/level/language planning | IP-003,006,021 |
| IP-008 | PLANNED | Questions, deterministic/rubric evaluators, misconception taxonomy, mastery algorithm | IP-007 |
| IP-009 | PLANNED | Teaching-session state machine, follow-ups, remediation/re-check, optimistic concurrency | IP-008 |
| IP-010 | PLANNED | SceneSpec and deterministic math/graph/code/timeline/diagram renderers | IP-007 |
| IP-011 | PLANNED | TTS, captions, avatar adapter, timeline composition/player, audio-only fallback | IP-009,010 |
| IP-012 | PLANNED | Final assessment, learning report, history/progress views | IP-008,009 |
| IP-013 | PLANNED | Learning paths, prerequisites, recommendation and spaced-review rules | IP-012 |
| IP-014 | PLANNED | Hindi/English/Hinglish QA, accessibility audit, safety/prompt-injection tests | IP-011–013 |
| IP-015 | PLANNED | Load/resilience/cost controls, provider fallbacks, backup/restore, and deletion verification | IP-014,023 |
| IP-016 | PLANNED | Production deployment, seed demo corpus, scripted 3–7 minute demo and technical disclosure | IP-015 |
| IP-017 | PLANNED | AgentPort, registry, task/result envelopes, artifact validators/store, workflow engine, context broker, budgets, and conformance harness | IP-001–003 |
| IP-018 | PLANNED | Implement knowledge specialists: ingestion, curator, retrieval, grounding/fact-check | IP-005–006,017 |
| IP-019 | PLANNED | Implement pedagogy/interaction specialists and secure learner observation/inference pipeline | IP-007–009,017 |
| IP-020 | PLANNED | Implement media specialists behind common contracts and end-to-end orchestrated fallback | IP-010–011,017 |
| IP-021 | PLANNED | Implement AI Gateway, capability/model router, prompt registry, provider configuration, health, rate/concurrency limits, usage, cost, and fallbacks | IP-001–003 |
| IP-022 | PLANNED | Implement LLM, embedding, reranking, image, STT, TTS, avatar/video, and OCR adapters with fakes and contract tests | IP-002,021 |
| IP-023 | PLANNED | Evaluate provider/model configurations for quality, grounding, multilingual behavior, latency, cost, safety, and failover; publish approval matrix | IP-021–022 |
| IP-024 | PLANNED | Produce third-party API/model/library/service disclosure with license/terms, data flow, retention, residency, limits, and operational ownership | IP-022–023 |

## Increment details

### Phase 0 — foundation

Build a vertical “hello lesson” slice through browser, FastAPI, orchestrator, fake specialist/provider, AI Gateway, artifact validator, database, queue, worker, and WebSocket event stream. Establish versioned agent/provider contracts before integrating real services. Exit only when one command starts local dependencies and CI runs format, lint, types, unit, integration, agent/provider conformance, frontend, and migration checks.

### Phase 1 — sources

Implement authorization before content features. Build streaming upload, lifecycle state, parsing fixtures for every format, OCR feature flag, deterministic chunks, then embeddings/retrieval. Exit with cross-tenant denial tests and a citation opening the correct page/slide.

### Phase 2 — intelligence

Use schema-first agent artifacts and provider fakes. Implement Learner Modeler, Curriculum, Planner, Explanation, Example, Quiz, Response Analyst, Adaptation, and Report specialists behind the orchestrator. Add fixed-seed evaluation cases for plan timing, learner level, language, groundedness, free-text grading, misconception classification, and changed-strategy remediation. Exit with a text/caption adaptive lesson and an auditable run graph so pedagogy is verified independently of media.

### Phase 3 — video

Implement Visual Planner/Renderer, Voice, Avatar, Composer, and Accessibility specialists. Render exact visuals with SVG, LaTeX, Matplotlib, or Mermaid; use provider adapters for images, speech, and avatar/video; compose short segments with FFmpeg. Exit with checkpoint-paused playback, captions/transcript, keyboard controls, and forced provider/media failure fallback.

### Phase 4 — outcomes

Keep attempts append-only, make mastery rebuildable, and show why a next step is recommended. Exit when a completed session influences a subsequent plan.

### Phase 5 — hardening

Run the PRD acceptance scenarios, AI evaluation gates, OWASP/upload fuzzing, queue burst tests, accessibility review, deletion/backup tests, and cost-budget rehearsal. Record actual providers/models/licenses and limitations before demo.

## Definition of done

- Acceptance criteria and negative/authorization paths pass.
- Migrations apply to empty and representative existing databases.
- New provider calls have timeout, error mapping, telemetry, fake, and contract tests.
- New agents have bounded responsibility, typed envelopes, context/privacy declaration, validators, conformance/evaluation tests, and no direct persistence or peer calls.
- New providers/models have approved configuration, license/terms and data-boundary review, evaluation evidence, budget, timeout/fallback policy, fake, and contract tests.
- AI changes pass versioned evaluation thresholds and retain prompt/model provenance.
- UI covers loading, empty, error, retry, offline/reconnect, and accessible keyboard states.
- No secret/private source content appears in commits, logs, or test snapshots.
- Relevant docs and feature status reflect reality.

## Parallelism and critical path

After the orchestrator/contract foundation, frontend shell, specialist implementations, provider fakes, and ingestion fixtures can proceed in parallel. The critical path is persistence/auth -> agent foundation -> knowledge agents -> pedagogy/interaction agents -> state machine -> media agents -> E2E hardening. Do not let avatar integration delay validation of adaptive pedagogy.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Provider latency, outage, or rate limits | Deadlines, circuit breakers, admission control, precomputation, approved fallback, visible degraded state |
| Hallucination | Hybrid retrieval, citation coverage checks, uncertainty, evaluation corpus |
| Free-text misgrading | Deterministic graders, explicit rubrics, confidence/clarification, audit |
| Demo cost/time | Quotas, pre-warmed demo source, cached assets, short segment generation |
| Scope pressure | Mandatory feature gate; defer advanced list until MVP passes |
| Multilingual quality | Native-speaker review set, provider/model evaluation matrix, and fallback disclosure |
| Vendor lock-in | Capability ports, contract tests, portable stored schemas, and at least one fake/fallback adapter |
| External data exposure | Purpose minimization, consent, provider review, encryption, retention/residency controls, redacted telemetry |
| Provider cost growth | Per-user budgets, quotas, caching, usage telemetry, alerts, and model-routing policy |
| Agent sprawl | Require a distinct contract, evaluation, security boundary, or scaling need; keep deterministic logic as code |
| Orchestration loops/cost | Finite workflow graph, hop/retry/deadline/token/cost bounds and cancellation |
| Conflicting specialist output | Predetermined authority, validators, immutable artifacts, no free-form voting |
| Learner inference harm | Separate facts/inferences, forbid sensitive diagnosis, require evidence/confidence/expiry and learner control |

## Change log

- 2026-08-31: replaced generic template with the initial AI Teacher implementation roadmap derived from the assessment.
- 2026-09-04: adopted the complete Next.js/FastAPI/provider-backed technology blueprint and superseded the local-only runtime workstream.

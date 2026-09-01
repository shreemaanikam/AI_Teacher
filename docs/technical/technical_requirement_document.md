# Technical Requirements Document

## Status and source of truth

This document defines implementation constraints for the planned AI Teacher. Product behavior is in `../product/project_requirement_document.md`, design in `architecture.md`, persistence in `backend_schema.md`, and actual completion in `../execution/features.md`. No application code exists as of 2026-08-31.

## Baseline stack

| Layer | Required baseline |
| --- | --- |
| Backend | Python 3.12+, Flask 3.x, Gunicorn in production |
| API schemas | Pydantic 2.x; OpenAPI generated and versioned |
| Async work | Celery 5.x with Redis 7.x broker/cache |
| Database | PostgreSQL 16+ with pgvector; SQLAlchemy 2.x and Alembic |
| Frontend | Node 22 LTS, TypeScript 5.x, React 19, Vite 7 |
| Object storage | S3-compatible API; MinIO locally |
| Testing | pytest, Vitest/Testing Library, Playwright; runtime/model contract and AI evaluation suites |
| Packaging | `pyproject.toml` with locked Python dependencies; `package-lock.json` |
| Deployment | OCI containers; Docker Compose locally; local/private-network production containers |

`llama.cpp` is the sole neural-model inference runtime. Hosted inference APIs are outside the approved architecture.

Minor versions are locked in implementation manifests. Upgrades require tests and, for breaking changes, a decision record.

## Service requirements

| ID | Requirement |
| --- | --- |
| TR-001 | Use an application factory and dependency injection at composition boundaries. |
| TR-002 | Separate API, service, domain, repository, AI, ingestion, media, and worker concerns. |
| TR-003 | API/worker processes are stateless; durable state lives only in PostgreSQL/object storage. |
| TR-004 | Local AI/media runtimes and storage services implement internal provider interfaces and normalize errors. |
| TR-005 | All LLM outputs used by code conform to versioned Pydantic/JSON schemas. Invalid output gets one repair attempt, then fails safely. |
| TR-006 | Long operations run as background jobs; requests return `202` plus job/resource identifiers. |
| TR-007 | Jobs are idempotent, bounded-retry, timeout-controlled, cancellable, observable, and dead-letterable. |
| TR-008 | Transactional state change plus outbox record occur atomically. |
| TR-009 | PostgreSQL migrations are forward-only, reviewed, and safe for existing rows. |
| TR-010 | UTC timestamptz is stored; BCP 47 tags identify language; UUIDv7 is preferred for public identifiers. |

## Multi-agent engine requirements

| ID | Requirement |
| --- | --- |
| AG-001 | The Master Teaching Orchestrator is an application service backed by a deterministic workflow/state machine; it is not an unrestricted supervisory prompt. |
| AG-002 | Specialists implement an `AgentPort[Input, Output]` and declare agent type/version, supported artifact types, timeout class, privacy scope, and capabilities. |
| AG-003 | Agents communicate only through the orchestrator using validated `AgentTaskEnvelope` and `AgentResultEnvelope` schemas. Direct agent-to-agent calls are prohibited. |
| AG-004 | Context is reference-based and least-privilege. An agent receives only fields/evidence required for its declared purpose, never database credentials or arbitrary repository access. |
| AG-005 | Agents cannot persist domain state. They return immutable candidate artifacts; an authorized service validates policy/schema/ownership and commits accepted artifacts. |
| AG-006 | Every run has `task_id`, `workflow_id`, `agent_type/version`, input/output schema versions, idempotency key, deadline, budget, trace ID, context references, result status, confidence, provenance, warnings, and redacted error. |
| AG-007 | The orchestrator enforces a finite execution graph, maximum attempts/hops, token/cost budgets, deadline propagation, cancellation, and loop prevention. |
| AG-008 | Agent output is untrusted until schema, policy, evidence, safety, and domain-invariant validators accept it. Invalid output cannot advance the teaching state. |
| AG-009 | Agent implementations may be deterministic code, a local `llama.cpp` workflow, or a hybrid, but must pass the same conformance and evaluation contract. Hosted model providers are prohibited. |
| AG-010 | Deployment location (in-process, Celery worker, authenticated service API) is hidden behind the same port; distributed IPC uses authenticated, encrypted, replay-safe messages. |
| AG-011 | Synchronous interactive paths invoke the minimum agent set. Planning/media work is precomputed asynchronously to meet latency budgets. |
| AG-012 | Agent/model/prompt rollout is versioned, observable, canaried, and independently reversible when stored artifact schemas remain compatible. |

### Specialist registry

| Group | Specialists | Required output |
| --- | --- | --- |
| Knowledge | Ingestion, Knowledge Curator, Retrieval, Grounding/Fact Check | normalized corpus, evidence packs, citation verdicts |
| Pedagogy | Learner Modeler, Curriculum, Lesson Planner, Explanation, Example | learner snapshot proposals, paths, plans, grounded teaching artifacts |
| Interaction | Quiz, Response Analyst, Adaptation, Report/Recommendation | questions/rubrics, evaluations, remediation strategy, outcomes |
| Media | Visual Planner, Visual Renderer, Voice, Avatar, Composer, Accessibility | SceneSpec, media assets, synchronized timeline, captions/alternatives |

Deterministic parsing, grading, rendering, and policy logic remains ordinary code even when exposed through an agent contract. “Agent” denotes a bounded capability, not necessarily another LLM call.

## Local inference and model supply chain

| ID | Requirement |
| --- | --- |
| LM-001 | Pin `llama.cpp` to an audited commit/build identifier; do not depend on a floating branch or unverified binary. |
| LM-002 | Ship separate tested runtime artifacts/profiles for `GGML_CUDA=ON`, `GGML_VULKAN=ON`, and CPU fallback. Backend detection is explicit and persisted. |
| LM-003 | Use `llama-server` behind an internal loopback/private interface. Agents call a Model Runtime Gateway, not `llama-server` directly. |
| LM-004 | Only GGUF architectures/features supported by the pinned `llama.cpp` build are eligible. Startup performs a model/backend capability probe and test inference. |
| LM-005 | A model manifest pins Hugging Face repository, immutable commit revision, filename, SHA-256, license, architecture, task, quantization, context size, chat template, tokenizer metadata, memory estimates, and evaluation version. |
| LM-006 | Downloads use the Hugging Face Hub with explicit consent, resumable transfer, temporary quarantine, checksum/signature where available, license gate, and atomic activation. Arbitrary URLs are prohibited. |
| LM-007 | Offline import uses the same allowlist, manifest, license, checksum, compatibility, malware, and evaluation gates as online download. |
| LM-008 | Fine-tuning occurs locally in an isolated training workspace. Approved base weights/datasets are pinned; data lineage, consent/license, recipe, seed, metrics, adapter, merge, GGUF conversion, quantization, and final checksum are reproducible. |
| LM-009 | Fine-tuning may use tooling other than `llama.cpp`; the deployed inference artifact must be supported GGUF and all production inference must run through `llama.cpp`. |
| LM-010 | The gateway manages model residency, shared instances, context/KV-cache budgets, GPU-layer offload, batching, concurrency, admission control, warmup, health, and eviction so logical agents do not load duplicate weights. |
| LM-011 | CUDA is selected only after a successful NVIDIA capability/VRAM probe. Vulkan is the portable GPU profile and must be validated on targeted Intel hardware. CPU fallback is always available. |
| LM-012 | Backend selection never changes the agent contract. Model/backend evaluation baselines detect unacceptable quantization or numerical quality regressions. |
| LM-013 | No cloud fallback exists. On model/backend failure, use an approved smaller local model, CPU fallback, deterministic implementation, or visible degraded/paused state. |
| LM-014 | Network egress from inference workers is denied after provisioning. Model download/fine-tuning processes are separated from serving processes. |
| LM-015 | Arbitrary TTS, diffusion, lip-sync, and video models are not assumed compatible with `llama.cpp`. They are permitted only after pinned-runtime compatibility and evaluation; otherwise use deterministic local media tooling/fallback. |

### Runtime profiles

| Profile | Target | Required validation |
| --- | --- | --- |
| `cuda` | Compatible NVIDIA RTX/other NVIDIA GPU | driver/toolkit/build compatibility, device/VRAM probe, backend tests, representative agent benchmark |
| `vulkan` | Vulkan-capable GPU, including targeted Intel Arc/iGPU devices | loader/driver/device probe, operation support, memory test, representative benchmark |
| `cpu` | Supported x86-64 baseline | ISA detection, thread/memory limit, representative benchmark |

Vulkan support does not guarantee acceptable performance on every Intel GPU. Publish a tested hardware matrix and select quantization, context, and concurrency from measured memory and latency.

## RAG and AI requirements

| ID | Requirement |
| --- | --- |
| AI-001 | Preserve source hierarchy and page/slide/offset provenance through parsing, chunking, retrieval, prompts, and citations. |
| AI-002 | Chunking is structure-aware with bounded overlap and deterministic checksums; embeddings are versioned. |
| AI-003 | Retrieval applies tenant/source ACL filters before hybrid search and reranking. |
| AI-004 | Prompts delimit retrieved content as data and explicitly reject instructions within it. |
| AI-005 | Planner output includes objectives, prerequisites, duration, segments, evidence, visuals, interactions, and assessment mappings. |
| AI-006 | Evaluation uses deterministic graders where possible and rubric-based model grading otherwise; confidence gates mastery changes. |
| AI-007 | Prompt template, model manifest/digest, llama.cpp build/backend, sampling parameters, evidence IDs, schema version, latency, and token usage are auditable. |
| AI-008 | AI regression datasets test grounding, citation, pedagogy, language, safety, and adaptation before prompt/model releases. |
| AI-009 | Topic-only knowledge is labeled separately from uploaded-source evidence; invented citations are prohibited. |
| AI-010 | Local model/backend fallback cannot silently change language, objectives, source scope, quality gate, or safety policy. |
| AI-011 | Learner-model output separates observations from inferences; each inference carries confidence, evidence references, sensitivity category, expiry, and algorithm/model version. |
| AI-012 | A grounding validator reviews material-derived teaching artifacts before publication; unsupported critical claims are rejected, revised, or labeled uncertain. |

## Media requirements

- A runtime-neutral `SceneSpec` is the source for visuals, narration, captions, and avatar cues.
- Deterministic subject visuals are preferred for exact content; generated images must be moderated and must not render equations/code relied on for correctness.
- Captions use a standard timed format (WebVTT at delivery), and every visual has transcript/alt-text representation.
- Media is stored by immutable key/checksum with MIME type, duration, dimensions, model/tool/runtime provenance, and generation version.
- Composition verifies audio/video duration drift and falls back to audio/captions/visuals when avatar output fails.

## API and realtime requirements

- REST paths begin `/api/v1`; request/response types appear in OpenAPI.
- RFC 9457 problem details represent errors; validation errors identify safe field paths.
- Mutating asynchronous endpoints accept `Idempotency-Key`.
- Cursor pagination is used for potentially growing collections.
- SSE is the baseline for job/session events; WebSocket is reserved for bidirectional realtime features.
- Clients reconnect using a last-event cursor and reconcile from authoritative REST state.
- Optimistic concurrency protects teaching-session transitions; duplicate responses return the original result or a conflict.

## Security and privacy requirements

- Validate ownership in the service/repository query, never solely in UI or route code.
- Use Argon2id password hashing, secure/HTTP-only/SameSite cookies, CSRF defense, TLS, and rate limiting.
- Restrict upload size/type/pages; sniff MIME, scan malware, isolate parsers, prevent zip/path traversal, and sanitize extracted HTML.
- Use short-lived signed object URLs. Do not expose storage/provider credentials.
- Load secrets from environment/secret manager; `.env.example` contains names only.
- Redact authorization, cookies, prompts, source content, personal data, and learner free text from default logs.
- Encrypt transport and managed storage; document data region and retention in deployment configuration.
- Account/document deletion immediately denies access and queues auditable physical deletion.
- Dependency, container, secret, SAST, and upload-fuzz scans run in CI.

## Performance and resilience budgets

| Concern | Target/control |
| --- | --- |
| Ordinary API latency | p95 < 500 ms excluding local model/background work |
| Topic plan | first usable plan target < 30 s on a documented recommended local profile |
| Progress | event within 2 s of a persisted job-state transition |
| llama-server calls | explicit connect/read timeout, admission/concurrency bulkhead, health circuit |
| Retry | exponential backoff with jitter only for classified transient failures |
| Database | indexed ownership/status/time queries; no unbounded lists or N+1 reads |
| Upload | configurable byte/page quotas and streaming transfer; no full file in API memory |
| Cost | per-operation token/media accounting, quotas, budget alerts, checksum caching |

## Frontend requirements

- React is a single responsive TypeScript client; server-rendered Flask is limited to health/error/bootstrap surfaces.
- Server state uses a query cache; lesson runtime uses a scoped state machine/store. Do not duplicate authoritative server data globally.
- The player supports keyboard controls, captions, transcript, reduced motion, audio-only mode, reconnection, and checkpoint focus management.
- Escape user/source content by default; sanitized Markdown uses an allowlist with external link protections.
- Route-level code splitting and lazy media loading are required; core setup remains usable at narrow mobile widths.

## Observability

Emit structured JSON logs with timestamp, severity, service, environment, trace ID, actor/resource IDs, event, duration, outcome, `llama.cpp` build, backend, model digest, tokens, and estimated compute where applicable. OpenTelemetry spans connect HTTP, queue, database, retrieval, and local runtime operations. Alerts cover queue age, job failure, API errors/latency, database saturation, model-server health, and resource exhaustion.

Agent metrics additionally include success/rejection/repair rate by agent version, schema failures, evidence coverage, confidence distribution, queue and execution time, orchestration hops, fallback frequency, token/media cost, and evaluator disagreement. Prompt or private context bodies are excluded from normal telemetry.

## Quality gates

Before merge: formatting, lint, type checking, unit/integration tests, schema/migration checks, frontend tests, dependency/secret scans. Before release: E2E acceptance, RAG/teaching evaluation thresholds, accessibility smoke tests, upload/security tests, backup restore verification, and staged deployment smoke tests.

The initial coverage target is 80% for domain/services with mandatory direct tests for authorization and state transitions; coverage never replaces behavior-based acceptance tests.

## Configuration and environments

Use `development`, `test`, `staging`, and `production`. Validate required configuration at startup. Separate databases, buckets, queues, keys, model caches, and runtime sockets per environment. Feature flags may switch approved model/backend profiles or experimental pedagogy but may not bypass authorization, safety, provenance, or schema validation.

## Repository contract

```text
app/  frontend/  migrations/  tests/  evals/  scripts/  docs/
compose.yaml  pyproject.toml  package.json  .env.example
```

Agent-specific layout:

```text
app/agents/contracts/       versioned envelopes and artifact schemas
app/agents/registry/        capabilities and deployment adapters
app/agents/specialists/     bounded implementations grouped by domain
app/agents/validators/      schema, evidence, safety, privacy, domain gates
app/orchestration/          workflow definitions, policies, budgets, context broker
tests/agent_contracts/      conformance tests shared by every implementation
evals/agents/               versioned quality/ablation datasets and thresholds
```

Generated media, uploads, secrets, local databases, and runtime caches are never committed. Significant deviations require an entry in `../decisions.md`.

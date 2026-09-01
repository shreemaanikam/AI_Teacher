# Architecture Decision Records

## Status

These decisions establish the initial target architecture on 2026-08-31. Because implementation has not started, they are `ACCEPTED` design constraints and must be revisited if prototype evidence invalidates them. Status values: `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, `REJECTED`.

## Index

| ID | Decision | Status |
| --- | --- | --- |
| ADR-001 | Modular monolith with asynchronous worker pools | ACCEPTED |
| ADR-002 | PostgreSQL with pgvector as authoritative store | ACCEPTED |
| ADR-003 | React TypeScript client and versioned Flask REST API | ACCEPTED |
| ADR-004 | Runtime-neutral agent and media adapters | ACCEPTED |
| ADR-005 | State-machine-controlled adaptive teaching | ACCEPTED |
| ADR-006 | Evidence-preserving hybrid RAG | ACCEPTED |
| ADR-007 | Segment timeline and SceneSpec for video teaching | ACCEPTED |
| ADR-008 | Schema-constrained, versioned AI contracts and evaluations | ACCEPTED |
| ADR-009 | Transactional outbox and idempotent jobs | ACCEPTED |
| ADR-010 | Append-only attempts with derived mastery | ACCEPTED |
| ADR-011 | Hub-and-spoke specialist agents under a deterministic master orchestrator | ACCEPTED |
| ADR-012 | Agents produce immutable artifacts and never persist domain state directly | ACCEPTED |
| ADR-013 | Logical agent modularity before physical microservices | ACCEPTED |
| ADR-014 | Separate learner observations from confidence-scored inferences | ACCEPTED |
| ADR-015 | llama.cpp is the sole neural inference runtime | ACCEPTED |
| ADR-016 | CUDA, Vulkan, and CPU are first-class local runtime profiles | ACCEPTED |
| ADR-017 | Verified Hugging Face or reproducible local fine-tune is the only model supply chain | ACCEPTED |

## ADR-001 — Modular monolith with asynchronous worker pools

**Context:** The prototype needs many domain capabilities but a small team and short delivery window. Parsing and avatar generation are slow and bursty.

**Decision:** Keep one modular Python codebase and relational model. Deploy stateless API/realtime processes plus Celery worker pools separated by ingestion, AI, and media queues.

**Why:** It minimizes distributed-system overhead while permitting independent scaling and failure isolation for heavy workloads.

**Consequences:** Module boundaries and provider ports must be enforced in code. A service split is justified only by measured scale, security isolation, or team ownership—not anticipation.

## ADR-002 — PostgreSQL with pgvector as authoritative store

**Context:** The generic documentation suggested SQLite or MongoDB, but AI Teacher needs relational ownership/state, transactions, full-text retrieval, and vector search together.

**Decision:** Use PostgreSQL 16+ with pgvector. Redis is ephemeral queue/cache; S3-compatible storage holds binaries.

**Alternatives:** SQLite lacks the intended concurrent/production workload; MongoDB weakens relational constraints and adds a separate vector/search story; a dedicated vector database adds operational complexity before scale evidence.

**Consequences:** Development requires containers. Vector scale must be load tested; a dedicated vector service remains possible behind the retrieval repository.

## ADR-003 — React TypeScript client and versioned Flask REST API

**Context:** The classroom has synchronized playback, checkpoints, reconnectable progress, and substantial client interaction.

**Decision:** Use a React/TypeScript SPA for product screens and Flask `/api/v1` REST endpoints. SSE is the baseline server event channel; WebSocket is deferred to true bidirectional realtime teaching.

**Consequences:** OpenAPI and shared/generated client types prevent drift. Simple bootstrap/health/error surfaces may remain server-rendered.

## ADR-004 — Runtime-neutral agent and media adapters

**Context:** Local models, deterministic tools, storage, OCR, voice, and avatar implementations differ in language, hardware, latency, and availability.

**Decision:** Domain/services depend on internal ports and normalized DTOs/errors. Local runtime/model/tool configuration is deployment-specific and recorded per generated result. Neural implementations additionally obey ADR-015.

**Consequences:** Adapters and contract tests add initial work but avoid runtime types in the domain and permit fakes and local fallbacks.

## ADR-005 — State-machine-controlled adaptive teaching

**Context:** A free-form agent may skip questions, loop, contradict state, or behave like a chatbot.

**Decision:** Persist a deterministic teaching-session state machine. Models propose structured plan/evaluation/remediation artifacts; application rules authorize transitions.

**Consequences:** Behavior is testable and resumable. New pedagogy requires explicit states/transitions instead of prompt-only changes.

## ADR-006 — Evidence-preserving hybrid RAG

**Context:** Uploaded-material teaching must minimize hallucinations and show exactly where claims came from.

**Decision:** Preserve document hierarchy/location through deterministic chunking; apply tenant/source filters, vector plus full-text retrieval, adjacency expansion, reranking, and segment-level citations. Topic-only knowledge is labeled separately.

**Consequences:** Ingestion metadata is richer and retrieval evaluation is mandatory. The system can decline or qualify low-evidence claims.

## ADR-007 — Segment timeline and SceneSpec for video teaching

**Context:** A single pre-rendered video cannot naturally pause, adapt, switch language, or recover partial generation.

**Decision:** Model lessons as independently rendered segments controlled by a runtime-neutral SceneSpec and timeline manifest. Prefer exact deterministic renderers and compose avatar, voice, captions, and visuals. Provide audio/caption/visual fallback.

**Consequences:** Playback orchestration is more complex than one MP4 but supports checkpoints, progressive readiness, caching, and local implementation replacement. Exported MP4 is optional.

## ADR-008 — Schema-constrained, versioned AI contracts and evaluations

**Context:** Model output is probabilistic and provider/model upgrades can silently regress teaching.

**Decision:** Parse all operational AI output into versioned Pydantic schemas, store prompt/model/evidence provenance, and gate releases with fixed RAG/pedagogy/language/safety evaluation sets.

**Consequences:** One bounded repair attempt is allowed for invalid structures; persistent failure is visible and retryable. Prompt changes are reviewed like code.

## ADR-009 — Transactional outbox and idempotent jobs

**Context:** Database commits and queue publishes can fail independently, and clients may retry mutations.

**Decision:** Commit state and outbox events atomically; dispatch them asynchronously. Jobs and external mutations use stable idempotency keys, bounded retries, heartbeats, cancellation, and dead-letter state.

**Consequences:** Extra tables/workers are required, but duplicate media, double session advancement, and lost work are controlled.

## ADR-010 — Append-only attempts with derived mastery

**Context:** Progress needs auditability and algorithms will evolve.

**Decision:** Preserve every learner response/evaluation as append-only evidence. Store a versioned mastery snapshot for fast reads that can be rebuilt.

**Consequences:** Storage grows and retention needs care. Algorithm changes can be tested/recomputed without rewriting historical answers.

## ADR-011 — Hub-and-spoke specialist agents under a deterministic master orchestrator

**Context:** Specialized knowledge, pedagogy, assessment, learner modeling, and media capabilities improve separation and independent evaluation, but free-form peer agents create loops, conflicts, unpredictable cost, and poor auditability.

**Decision:** Use a Master Teaching Orchestrator backed by a versioned workflow/state machine. It delegates bounded tasks through typed envelopes. Specialists return to the orchestrator and may not call peers directly. Predetermined authority and validators resolve output—not open-ended agent debate.

**Alternatives:** A single large teaching prompt is simpler but tightly coupled and difficult to evaluate. Peer-to-peer agent chat appears flexible but is hard to secure, bound, replay, and debug.

**Consequences:** The engine is traceable, budgetable, and modular, but requires an agent registry, contracts, artifact validation, context broker, and orchestration tests.

## ADR-012 — Agents produce immutable artifacts and never persist domain state directly

**Context:** Giving autonomous agents database access mixes probabilistic reasoning with authorization, validation, and transactions.

**Decision:** An agent receives a purpose-scoped projection and returns an immutable candidate artifact. The owning application service validates schema, evidence, safety, ownership, and invariants before accepting and persisting it. Agents never receive database credentials.

**Consequences:** More explicit DTOs and validation steps are required. Failed/rejected output cannot corrupt authoritative state, and provenance remains inspectable.

## ADR-013 — Logical agent modularity before physical microservices

**Context:** Extreme modularity is valuable, but independently deploying every specialist on day one would create network, operations, security, and release overhead.

**Decision:** Every specialist implements the same deployment-independent `AgentPort`. Initially run most specialists in the modular monolith/Celery worker pools. Move selected implementations behind authenticated APIs only for measured scaling, dependency isolation, security, or team ownership reasons.

**Consequences:** Architecture remains replaceable without premature distribution. Conformance tests must ensure in-process, worker, and remote adapters behave equivalently.

## ADR-014 — Separate learner observations from confidence-scored inferences

**Context:** Personalization needs a learner model, but AI-generated profiles can be incorrect, sensitive, or overly permanent.

**Decision:** Store immutable educational observations separately from inferred traits. An inference needs evidence references, confidence, version, educational sensitivity classification, expiry/review state, and learner correction/deletion support. Prohibit medical, psychological, demographic, and unrelated sensitive diagnosis.

**Consequences:** Planning uses a curated learner snapshot rather than raw history. Personalization is more explainable and correctable but requires additional schema, policy, and UX.

## ADR-015 — llama.cpp is the sole neural inference runtime

**Context:** Local privacy and deployment independence are primary requirements. Multiple neural runtimes would multiply GPU memory, packaging, security, and compatibility complexity.

**Decision:** Every production neural model must be a supported GGUF artifact executed locally by a pinned `llama.cpp`/`llama-server` build through the Model Runtime Gateway. Hosted inference and silent cloud fallback are prohibited. Non-neural deterministic tools are unaffected.

**Alternatives:** Cloud APIs simplify access to high-end models but violate local-only operation. Multiple local runtimes expand model coverage but weaken the single-runtime operational guarantee.

**Consequences:** Text, embedding, reranking, and supported multimodal agents share one operational layer. Arbitrary TTS/diffusion/lip-sync/video architectures cannot be assumed; unsupported neural media uses deterministic/accessibility fallback until `llama.cpp` supports an evaluated GGUF equivalent.

## ADR-016 — CUDA, Vulkan, and CPU are first-class local runtime profiles

**Context:** Users may have NVIDIA RTX GPUs, Intel Arc/integrated GPUs, or no compatible GPU.

**Decision:** Build and test separate CUDA, Vulkan, and CPU `llama.cpp` artifacts. Prefer validated CUDA on NVIDIA, validated Vulkan on targeted Intel/other devices, and retain CPU fallback. Hardware probing selects only an approved model/backend profile.

**Consequences:** Releases require a hardware/driver test matrix and backend-specific performance/quality evaluation. Vulkan support does not promise acceptable performance on every Intel device.

## ADR-017 — Verified Hugging Face or reproducible local fine-tune is the only model supply chain

**Context:** Model files are executable-like high-impact artifacts with license, provenance, integrity, compatibility, and safety risk.

**Decision:** Pretrained artifacts come only from allowlisted Hugging Face repositories pinned to immutable revisions, or from the project's reproducible local fine-tuning pipeline. Every artifact is quarantined, hashed, license-checked, inspected, evaluated, converted/quantized to supported GGUF when necessary, and atomically activated with a model card/manifest.

**Consequences:** Setup is slower and model choice curated. Arbitrary URLs and untracked weights are rejected; offline import follows the same gates. Fine-tuning frameworks may differ, but deployed inference remains llama.cpp-only.

## ADR-018 — Agora is an optional RTC transport, not an inference runtime

**Context:** Interactive lessons benefit from low-latency learner media and interruption-ready delivery, but the approved architecture requires neural inference to remain local and fully provisioned lessons to retain an offline mode.

**Decision:** Integrate Agora Web RTC 4.x behind application-owned adapters for opt-in live audio/video. Keep teaching state, captions, checkpoints, source data, orchestration, and neural inference on project infrastructure. Do not adopt Agora Conversational AI Engine in the approved local-only profile. Preserve composed timeline playback as the default/degraded path.

**Consequences:** Live RTC requires internet access, disclosure/consent, residency review, short-lived server-issued tokens, and cost controls. The adapter remains replaceable and an Agora outage cannot remove transcript/visual lesson access. This partially supersedes ADR-003 only for live media; SSE remains the authoritative server-event baseline.

**Status:** Accepted, 2026-09-01.

## Decision process

New significant choices record context, decision, alternatives, consequences, related features/tasks, date, and status here. Never edit an accepted decision to hide history; mark it superseded and add its replacement.

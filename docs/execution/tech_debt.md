# Technical Debt and Risk Register

## Purpose

This register distinguishes intentional shortcuts from unresolved design choices. Since implementation has not started, entries are anticipated risks, not claims about existing code. Use `OPEN`, `ACCEPTED`, `IN_PROGRESS`, or `RESOLVED`.

| ID | Status | Item | Impact | Planned treatment / trigger |
| --- | --- | --- | --- | --- |
| TD-001 | OPEN | Local GGUF models/quantizations for each capability are not selected or benchmarked. | Quality, latency, memory, and multilingual behavior are uncertain. | Benchmark approved Hugging Face/local fine-tunes across CUDA, Vulkan, and CPU during IP-023. |
| TD-002 | ACCEPTED | MVP uses composed segments rather than continuous real-time photorealistic video. | Transitions may feel less natural. | Preserve runtime-neutral SceneSpec; reconsider after mandatory adaptive flow is reliable. |
| TD-003 | OPEN | Hindi/Hinglish evaluation corpus and native-speaker review are not available. | Fluency and grading bias may escape automated tests. | Create reviewed examples before multilingual release acceptance. |
| TD-004 | OPEN | Mastery update formula has not been empirically calibrated. | Recommendations may over/underestimate learning. | Version the algorithm; analyze pilot attempts and compare educator judgments. |
| TD-005 | OPEN | OCR quality varies for equations, handwriting, and complex layouts. | Missing or incorrect source evidence. | Capture OCR confidence, show warnings, permit page exclusion/reprocess, benchmark samples. |
| TD-006 | OPEN | Generated visual correctness lacks an automated domain validator. | Misleading science/math visuals. | Prefer deterministic renderers; require citation/alt text; add subject-specific validators. |
| TD-007 | OPEN | Data retention and residency values are deployment-dependent. | Privacy/compliance cannot be finalized globally. | Require explicit production configuration and privacy review before external users. |
| TD-008 | ACCEPTED | Modular monolith is initially a single deployable codebase. | Independent scaling is limited beyond worker queues. | Split a service only when measured load, team ownership, or isolation requires it. |
| TD-009 | OPEN | pgvector scaling limits are unmeasured for large multi-tenant corpora. | Retrieval latency may grow. | Load test; partition/index tune; consider external vector service only on evidence. |
| TD-010 | OPEN | AI evaluation thresholds and golden dataset are not yet defined. | Prompt/model regressions could ship unnoticed. | IP-003/IP-006 establish versioned datasets and release thresholds. |
| TD-011 | OPEN | Agent granularity and the minimum interactive critical path are not benchmarked. | Agent sprawl could increase latency, cost, and failure rate without quality gain. | Prototype coarse specialists first; split only when contract/evaluation/scaling evidence justifies it. |
| TD-012 | OPEN | Workflow/orchestration technology is not selected beyond the initial service abstraction. | Celery alone may become awkward for long-lived durable workflows. | Benchmark the documented port with Celery; consider Temporal or equivalent when recovery/versioning needs are proven. |
| TD-013 | OPEN | Learner inference taxonomy, expiry, and correction UX require educator/privacy review. | Incorrect or sensitive profiles could harm personalization and trust. | Limit MVP to concept-level educational inferences and complete review before external use. |
| TD-014 | ACCEPTED | Logical agents initially share a deployable codebase and worker infrastructure. | Process-level isolation and independent releases are limited. | Keep strict ports/contracts; extract only for measured scale, security, dependency, or team boundary. |
| TD-015 | OPEN | Multi-agent quality gain over a smaller pipeline is not yet experimentally established. | Complexity may not improve teaching outcomes. | Run ablations comparing specialist pipeline, merged agents, and baseline using cost/latency/pedagogy metrics. |
| TD-016 | OPEN | Targeted Intel Vulkan device/driver coverage is not defined. | “Intel GPU support” could be misleading and performance may be unusable on low-memory iGPUs. | Define and publish a measured compatibility matrix; treat untested devices as CPU-fallback only. |
| TD-017 | OPEN | llama.cpp-compatible high-quality TTS/avatar/video models may not exist for required languages and hardware. | Mandatory human-like media quality may be reduced under the sole-runtime constraint. | Validate support early; prioritize deterministic local voice/2D animation and accessible transcript fallback; revisit scope explicitly if assessment cannot be met. |
| TD-018 | OPEN | Fine-tuning datasets and licensing/consent are not selected. | Training could introduce legal, privacy, bias, or reproducibility risk. | Require dataset cards, provenance review, dedup/redaction, held-out evaluations, and model cards before training. |
| TD-019 | OPEN | Quantization quality drift across tasks/backends is unmeasured. | Smaller models may fit hardware but degrade grading or teaching accuracy. | Maintain task/backend-specific gates; do not approve one quantization globally from a single benchmark. |
| TD-020 | OPEN | Agora bootstrap uses a Console-issued temporary RTC token and has no authenticated lesson ownership layer yet. | Shared/expired tokens are unsuitable for production and Agora RTC creates an external privacy/network boundary. | Replace with authorized server-side AccessToken2 issuance, renewal, consent, residency review, and abuse controls before external use. |

## Maintenance rule

Every intentional compromise introduced during implementation gets an owner, evidence of impact, remediation, and review trigger. Provider limitations that affect observable behavior also appear in the relevant feature entry and user-facing release notes.

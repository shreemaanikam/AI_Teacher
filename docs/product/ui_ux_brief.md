# UI / UX Brief

## Experience direction

The product should feel like a calm, attentive digital classroom—not a chatbot dashboard or a video editor. The teacher, educational visual, and current learning action share the stage. The interface is warm and credible, with low cognitive load, visible grounding, and clear learner control.

Design priorities:

1. Orient the learner: topic, objective, position, and next action are always clear.
2. Make interaction feel safe: mistakes invite explanation, not punishment.
3. Keep video accessible: captions, transcript, keyboard, audio-only, and reduced motion are first-class.
4. Reveal system work honestly: upload/media stages, evidence, uncertainty, retry, and fallback.
5. Preserve focus: advanced settings and operational detail stay secondary.
6. Make multi-agent work trustworthy without anthropomorphizing internal automation or exposing chain-of-thought.

## Visual system

Use design tokens; values are the initial accessible baseline.

| Role | Light | Dark |
| --- | --- | --- |
| Canvas | `#F7F8F5` | `#101614` |
| Surface | `#FFFFFF` | `#17201D` |
| Primary / teacher | `#146B55` | `#63D1AC` |
| Primary hover | `#0F5644` | `#84DEC0` |
| Accent / learning | `#5B4BC4` | `#A99DFF` |
| Text | `#17211E` | `#F3F7F5` |
| Muted text | `#52615C` | `#BAC6C1` |
| Border | `#D8E0DC` | `#35433E` |
| Success | `#237A49` | `#6ED69A` |
| Warning | `#9A5A00` | `#F6BC63` |
| Error | `#B3261E` | `#FF8A83` |

Never communicate answer state or progress by color alone. Use text/icon/shape. Body contrast targets WCAG AA. Respect system theme and store the learner's explicit override.

- Typography: `Inter` for Latin UI and `Noto Sans Devanagari` fallback for Hindi; system sans fallback. Math uses KaTeX fonts; code uses a legible monospace.
- Base text: 16 px, 1.5 line height. Reading transcript: 18 px on wide screens. Avoid body text below 14 px.
- Spacing: 4 px base scale (`4, 8, 12, 16, 24, 32, 48`).
- Radius: 8 px controls, 12 px cards, 16 px major panels. Shadows are subtle and never the only boundary.
- Motion: 150–250 ms for state continuity; no decorative avatar motion when reduced motion is enabled.

## Responsive shell

- Mobile `<768px`: single column, bottom primary navigation, visual/teacher stage above controls, transcript/checkpoint in a sheet; no hover dependency.
- Tablet `768–1199px`: stage above or beside collapsible lesson outline.
- Desktop `>=1200px`: three zones—outline (20%), teaching stage (50–60%), transcript/interaction (remaining). Panels can collapse to enlarge content.
- Content max width is 1440 px; reading text max width is about 72 characters.

## Key screens

### Dashboard

Lead with `Continue lesson` when resumable, otherwise `Start learning`. Show a small set of recommendations with “why this” reasoning, recent reports, and source-processing alerts. A new learner sees one guided empty state, not empty analytics.

### Library and upload

Use drag/drop plus visible file button. Before selection show formats and configured limit. Each file row has name, size, language, stage, progress, retry/replace/delete, and accessible status announcements. Never show indefinite “Processing” without stage or updated time.

### Lesson setup

Use a focused step flow:

1. `What do you want to learn?` Topic or ready source/section.
2. `Make it yours` objective, level/prior knowledge, teaching language/style.
3. `Plan your time` minutes/days, depth, interaction frequency.
4. Review an estimate and create.

Profile defaults prefill but remain overridable. Advanced settings are collapsed. The primary action states the outcome: `Create my 20-minute lesson`.

### Preparation

Show meaningful milestones: understanding source, planning, creating explanations, rendering visuals, generating voice/avatar, final checks. Segments ready for safe progressive playback may be exposed. Provide cancel and background notification; failures identify the affected component and fallback.

The learner sees outcome-oriented stages, not a noisy list of internal agents. A compact `How this lesson was created` disclosure may show specialized knowledge, teaching, assessment, and media contributions together with local model digest, quantization, backend, and source disclosures.

### Local model setup

Model management is an administrative/setup surface, not part of normal classroom complexity. It shows:

- detected CPU/GPU, selected `CUDA`, `Vulkan`, or `CPU` profile, and whether the exact device/driver is tested;
- recommended GGUF bundle with task, quantization, context, size, RAM/VRAM estimate, expected performance tier, source revision, license, and limitations;
- explicit `Download and activate`, `Import offline`, pause/resume, quarantine/verification/evaluation stages, and safe removal;
- health, resident model, memory use, queue/admission status, and local-only/network-isolated indicator;
- clear language that Vulkan capability does not guarantee high performance and CPU fallback may be slower.

Never download weights because a learner pressed `Create lesson`. License acceptance and large storage use require a separate informed action. Do not claim a model is secure or compatible merely because it is GGUF; show verification and evaluation status.

### Interactive classroom

The stage contains:

- lesson title, objective breadcrumb, segment progress and time remaining;
- dominant educational visual, with avatar placed so it never covers labels/captions;
- play/pause, seek over completed segments, volume, speed, captions, language, fullscreen;
- collapsible outline and citation-aware transcript;
- persistent `Ask a question` action;
- checkpoint panel that pauses media and owns focus.

The avatar is supportive, not visually dominant. Exact equations/code/diagrams receive more space than the presenter. The transcript highlights the current sentence and exposes citations as buttons opening a source drawer at page/slide context.

### Checkpoint and remediation

Use neutral language: “Let’s check this idea.” On incorrect answers say what reasoning to revisit and offer an alternative representation; avoid red full-screen failure states. Show attempt/hint status. During evaluation, retain the answer but disable duplicate submission. Re-check questions must not appear identical.

### Report and progress

Report hierarchy: completion message; score with context; objectives demonstrated; strengths; concepts to revisit; citations/attempt review; recommended next action. Charts always have text/table equivalents and avoid implying false precision. Mastery labels (`Starting`, `Developing`, `Secure`) accompany numeric internal scores.

## Components and states

| Component | Required behavior/states |
| --- | --- |
| `AsyncStatus` | queued, staged progress, delayed, failed/retry, cancelled, ready; ARIA live throttled |
| `SourcePicker` | topic/source modes, search, processing-disabled items, scope preview |
| `LessonTimeline` | current/completed/locked/checkpoint/remediation, keyboard navigation |
| `TeachingStage` | visual/avatar/audio/caption fallback and loading skeleton with fixed aspect ratio |
| `Transcript` | timed highlight, search, citation buttons, language labels, copy restrictions if required |
| `CheckpointCard` | prompt, response controls, validation, submitting, feedback, clarify, re-check |
| `CitationDrawer` | source title/location/excerpt, previous/next citation, inaccessible/deleted state |
| `RecommendationCard` | action, reason, estimated time, prerequisite/weakness context |

All async components implement default, loading, empty, error, retry, success, offline/reconnecting, and permission-safe states when applicable. Skeletons mimic stable layout; spinners alone are insufficient for long jobs.

## Accessibility

- Target WCAG 2.2 AA. All core tasks work by keyboard and at 200% zoom/reflow.
- Use semantic headings/landmarks, labels, descriptions, error summaries, and visible focus.
- On checkpoint pause, move focus to its heading; after feedback, announce result and focus the next meaningful action. Restore focus when drawers/dialogs close.
- Provide accurate synchronized captions, searchable transcript, audio descriptions/alt text for meaningful visuals, and audio-only/non-avatar mode.
- Touch targets are at least 44×44 CSS px where practical.
- Timed questions are off by default; learners can extend/disable timers.
- Do not auto-play audio on initial page load. Respect reduced motion, contrast, text spacing, and screen-reader announcements.

## Content voice

Teacher copy is concise, encouraging, specific, and age/level appropriate. Prefer “Let’s look at why” over “Wrong.” Distinguish `lesson`, `session`, `source`, `checkpoint`, `assessment`, and `learning path` consistently. Display dates in the user's locale and store UTC; durations use human-readable minutes/hours.

## Safety and trust UX

- Material lessons show citations and a clear source scope.
- Topic mode states that explanations use general AI knowledge.
- Uncertain/low-evidence output says so and offers source review.
- AI-generated visuals and avatar are disclosed without repetitive badges.
- State that inference is local and distinguish it from the one-time Hugging Face model download. Do not imply offline operation until required models are installed and a network-blocked health check passes.
- Destructive actions state affected sources/lessons and require confirmation; account deletion requires re-authentication.
- Do not use manipulative streaks, shame, or inaccessible countdown pressure.
- Never present learner inferences as objective identity claims. Use language such as “Based on your recent answers, you may want to revisit…” and provide `Why am I seeing this?`, correction, and deletion controls.
- Technical reviewers/admins may inspect a redacted agent run graph showing artifact lineage, versions, validation, latency, and cost. Never display hidden chain-of-thought, secrets, raw private context, or unrestricted learner history.
- Do not give every specialist a fictional personality in the core product. The single teacher persona remains consistent even though specialized agents work behind it.

## UX acceptance checklist

- Complete upload-to-report at 360 px and desktop widths.
- Use classroom without pointer, sound, avatar motion, or color perception.
- Reload/reconnect without duplicate response or lost typed answer.
- Understand every long-running state and recovery action.
- Switch Hindi/English with no clipped Devanagari, broken focus, or lost position.
- Avatar failure still yields a coherent lesson.

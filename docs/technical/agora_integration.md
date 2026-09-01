# Agora realtime integration

## Decision summary

Agora Web SDK 4.x is an optional RTC transport for learner audio/video and a future locally produced teacher stream. It does not replace the orchestrator, local `llama.cpp` inference, state machine, SceneSpec timeline, SSE progress, or local media fallbacks.

Agora Conversational AI Engine is deliberately not enabled: its managed ASR/TTS/avatar path conflicts with FR-070, FR-075, and NFR-015. A deployment using Agora RTC is no longer fully offline because media and operational metadata traverse Agora infrastructure. Obtain consent, disclose that boundary, and retain the non-Agora composed lesson mode.

## Implemented slice

- `frontend/src/features/lesson/agora.ts` owns the Agora SDK adapter.
- `RealtimeClassroom.tsx` joins/leaves, publishes camera/microphone, subscribes to participants, and cleans up tracks.
- `POST /api/v1/realtime/agora/credentials` validates channel/UID input behind a provider port.
- `EnvironmentAgoraCredentialsProvider` supports Console temporary tokens for local development only.

## Setup

1. Create an Agora project and enable Video Calling/RTC.
2. Copy `.env.example` to `.env`. Set `AGORA_APP_ID` and a channel/UID-matching `AGORA_TEMP_TOKEN` when certificate authentication is enabled.
3. Install Python and frontend dependencies, then run Flask and Vite with `/api` proxied to Flask.

Never put the App Certificate in `frontend`, a `VITE_*` variable, logs, or API responses.

## Production gates

- Mint AccessToken2 server-side after authenticating the learner and authorizing the lesson/channel.
- Derive opaque channels server-side, bind UID to the session, rate-limit issuance, keep TTL short, and audit without storing tokens.
- Renew on `token-privilege-will-expire` and fail closed on identity mismatch.
- Add consent, privacy/residency review, firewall testing, telemetry controls, and retention documentation.
- Stream only approved local teacher media; never send prompts, sources, learner profiles, or model traffic to Agora.
- Keep captions, checkpoints, and lesson state on authenticated application APIs; RTC is not authoritative state.


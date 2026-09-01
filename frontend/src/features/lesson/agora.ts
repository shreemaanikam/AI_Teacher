import AgoraRTC, { type IAgoraRTCClient, type IAgoraRTCRemoteUser, type ICameraVideoTrack, type IMicrophoneAudioTrack } from "agora-rtc-sdk-ng";

export type ConnectionState = "idle" | "joining" | "joined" | "leaving" | "error";
export interface AgoraCredentials { app_id: string; channel: string; uid: number; token: string | null; expires_at: string }
export interface LocalTracks { microphone: IMicrophoneAudioTrack; camera: ICameraVideoTrack }

export function createAgoraClient(): IAgoraRTCClient {
  return AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });
}

export async function fetchCredentials(channel: string, uid: number): Promise<AgoraCredentials> {
  const response = await fetch("/api/v1/realtime/agora/credentials", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel, uid, role: "publisher" }),
  });
  if (!response.ok) throw new Error(`Could not obtain Agora credentials (${response.status})`);
  return response.json() as Promise<AgoraCredentials>;
}

export async function createLocalTracks(): Promise<LocalTracks> {
  const [microphone, camera] = await AgoraRTC.createMicrophoneAndCameraTracks();
  return { microphone, camera };
}

export async function subscribeToUser(client: IAgoraRTCClient, user: IAgoraRTCRemoteUser, mediaType: "audio" | "video") {
  await client.subscribe(user, mediaType);
  if (mediaType === "audio") user.audioTrack?.play();
}

export function closeTracks(tracks: LocalTracks | null) {
  tracks?.microphone.close();
  tracks?.camera.close();
}


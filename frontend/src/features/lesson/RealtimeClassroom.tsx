import { useCallback, useEffect, useRef, useState } from "react";
import type { IAgoraRTCRemoteUser } from "agora-rtc-sdk-ng";
import { closeTracks, createAgoraClient, createLocalTracks, fetchCredentials, subscribeToUser, type ConnectionState, type LocalTracks } from "./agora";

interface Props { channel: string; uid: number }

export function RealtimeClassroom({ channel, uid }: Props) {
  const [client] = useState(createAgoraClient);
  const tracksRef = useRef<LocalTracks | null>(null);
  const localVideoRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<ConnectionState>("idle");
  const [remoteUsers, setRemoteUsers] = useState<IAgoraRTCRemoteUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  const leave = useCallback(async () => {
    if (state === "idle") return;
    setState("leaving");
    closeTracks(tracksRef.current);
    tracksRef.current = null;
    await client.leave();
    setRemoteUsers([]);
    setState("idle");
  }, [client, state]);

  useEffect(() => {
    const published = (user: IAgoraRTCRemoteUser, mediaType: "audio" | "video") => {
      void subscribeToUser(client, user, mediaType).then(() => setRemoteUsers([...client.remoteUsers]));
    };
    const changed = () => setRemoteUsers([...client.remoteUsers]);
    client.on("user-published", published);
    client.on("user-unpublished", changed);
    client.on("user-left", changed);
    return () => {
      client.off("user-published", published);
      client.off("user-unpublished", changed);
      client.off("user-left", changed);
      closeTracks(tracksRef.current);
      void client.leave();
    };
  }, [client]);

  const join = async () => {
    try {
      setError(null); setState("joining");
      const credentials = await fetchCredentials(channel, uid);
      await client.join(credentials.app_id, credentials.channel, credentials.token, credentials.uid);
      const tracks = await createLocalTracks();
      tracksRef.current = tracks;
      tracks.camera.play(localVideoRef.current!);
      await client.publish([tracks.microphone, tracks.camera]);
      setState("joined");
    } catch (cause) {
      closeTracks(tracksRef.current); tracksRef.current = null;
      await client.leave();
      setError(cause instanceof Error ? cause.message : "Could not join the classroom");
      setState("error");
    }
  };

  return <main className="classroom">
    <header><p className="eyebrow">LIVE LESSON</p><h1>Your AI classroom</h1><p>Agora carries real-time media; lesson reasoning stays on the local teacher runtime.</p></header>
    <section className="stage" aria-label="Classroom video">
      <div className="teacher-tile"><div className="orb" /><strong>AI Teacher</strong><span>Waiting for the local teacher stream</span></div>
      <div className="video-tile"><div ref={localVideoRef} className="video" /><span>You</span></div>
      {remoteUsers.map((user) => <RemoteVideo key={String(user.uid)} user={user} />)}
    </section>
    <footer><span className={`status status-${state}`}>{state}</span>
      {state === "joined" ? <button onClick={() => void leave()}>Leave lesson</button> : <button disabled={state === "joining" || state === "leaving"} onClick={() => void join()}>Join lesson</button>}
      {error && <p role="alert">{error}</p>}
    </footer>
  </main>;
}

function RemoteVideo({ user }: { user: IAgoraRTCRemoteUser }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { if (ref.current && user.videoTrack) user.videoTrack.play(ref.current); return () => user.videoTrack?.stop(); }, [user, user.videoTrack]);
  return <div className="video-tile"><div ref={ref} className="video" /><span>Participant {String(user.uid)}</span></div>;
}

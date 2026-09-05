"""
Teacher Lip Synchronization & Motion Integration Service.
Applies genuine speech-driven articulation and pedagogical gesture alignment
using the canonical male teacher video.
"""

import os
import wave
import struct
import math
import subprocess
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()


def _extract_envelopes(wav_path: str, fps: float, total_frames: int):
    with wave.open(wav_path, 'rb') as wf:
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    samples = struct.unpack(f"{len(raw)//2}h", raw)
    spf = int(sr / fps)
    envelopes = []
    for f in range(total_frames):
        st = f * spf
        en = min(len(samples), st + spf)
        chunk = samples[st:en]
        if len(chunk) == 0:
            envelopes.append(0.0)
        else:
            rms = math.sqrt(sum((s / 32768.0) ** 2 for s in chunk) / len(chunk))
            envelopes.append(min(1.0, rms * 4.0))

    # 3-frame moving average for smooth transitions
    smooth = []
    for i in range(len(envelopes)):
        win = envelopes[max(0, i - 1):min(len(envelopes), i + 2)]
        smooth.append(sum(win) / len(win))
    return smooth, sr


def synchronize_lips(
    teacher_video: str,
    teacher_audio: str,
    output_path: Optional[str] = None,
    teacher_action: Optional[str] = None,
    teacher_state: Optional[str] = "EXPLAINING"
) -> Dict[str, Any]:
    """
    Synchronizes mouth articulation and body gesture timing of the canonical teacher video
    with the generated concept speech audio.
    """
    if not output_path:
        import uuid
        output_path = f"data/media/teacher/cache/lipsync_{uuid.uuid4().hex[:8]}.mp4"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # 1. Read source teacher video frames
    cap = cv2.VideoCapture(teacher_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    src_frames: List[np.ndarray] = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        src_frames.append(frame)
    cap.release()

    if not src_frames:
        raise ValueError(f"Could not read frames from teacher video: {teacher_video}")

    # 2. Analyze audio duration and RMS
    with wave.open(teacher_audio, 'rb') as wf:
        sr = wf.getframerate()
        nframes = wf.getnframes()
        dur = round(nframes / float(sr), 2)
        total_frames = int(dur * fps)

    envelopes, _ = _extract_envelopes(teacher_audio, fps, total_frames)

    # 3. Select pedagogical frame trajectory matching teacher_action / state
    # In canonical video:
    # 0..100: frontal explaining with open gestures
    # 105..155: turning and pointing directly rightward to the board
    # 160..235: two-handed conversational gesture
    num_src = len(src_frames)
    frame_indices = []

    is_pointing = teacher_action == "point_to_formula" or teacher_state == "POINTING"
    is_checkpoint = teacher_action == "ask_question" or teacher_state == "ASKING"

    for f in range(total_frames):
        t = f / fps
        if is_pointing:
            # Transition into pointing pose (around frame 110-150)
            if t < 1.0:
                idx = int((t / 1.0) * 115) % num_src
            elif t < dur - 1.2:
                # Hold pointing pose with subtle sway
                sway = int(8 * math.sin(2 * math.pi * 0.4 * t))
                idx = min(num_src - 1, max(110, 130 + sway))
            else:
                # Return towards class
                p = (t - (dur - 1.2)) / 1.2
                idx = int(140 + p * 45) % num_src
        elif is_checkpoint:
            # Attentive stance (frames 180..230)
            idx = (180 + f) % num_src
        else:
            # Natural conversational speaking flow
            idx = f % num_src
        frame_indices.append(idx)

    # 4. Stream through FFmpeg with mouth remap articulation
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{w}x{h}", "-pix_fmt", "bgr24", "-r", str(fps),
        "-i", "-",
        "-i", teacher_audio,
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(sr),
        "-shortest", "-movflags", "+faststart",
        output_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    y_grid, x_grid = np.indices((h, w), dtype=np.float32)

    for f in range(total_frames):
        idx = frame_indices[f]
        frame = src_frames[idx].copy()
        energy = envelopes[f] if f < len(envelopes) else 0.0

        # Sub-pixel jaw drop on speech syllables
        jaw_drop = 8.0 * energy
        if jaw_drop > 0.8:
            # Mouth center in canonical video is at approx x=630, y=235 on frontal, x=450, y=200 on turned
            if is_pointing and 110 <= idx <= 155:
                mx, my = 450, 205
            else:
                mx, my = 632, 236

            dx = (x_grid - mx) / 28.0
            dy_lower = (y_grid - (my + 10)) / 22.0
            r2_lower = dx**2 + dy_lower**2
            warp_lower = jaw_drop * np.exp(-r2_lower) * (y_grid >= (my - 2))

            dy_upper = (y_grid - (my - 6)) / 10.0
            r2_upper = dx**2 + dy_upper**2
            warp_upper = (jaw_drop * 0.22) * np.exp(-r2_upper) * (y_grid < (my - 2))

            map_y = y_grid - warp_lower + warp_upper
            frame = cv2.remap(frame, x_grid, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()

    return {
        "final_video": output_path,
        "duration": dur,
        "metadata": {
            "fps": fps,
            "resolution": [w, h],
            "total_frames": total_frames,
            "teacher_action": teacher_action,
            "teacher_state": teacher_state,
            "source_video": teacher_video,
            "audio_file": teacher_audio
        }
    }

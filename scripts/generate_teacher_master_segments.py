"""
Master Teacher Video Segment Generator.
Generates all 6 college physics Ohm's Law teaching segments with:
- Authentic gesture poses (open hands, pointing to board, podium lecture)
- Natural eye blinking and head sway micro-movements
- Audio-synchronized viseme lip movement
- Muxed H.264 video + AAC audio streams with +faststart
- Distribution to app/static, frontend/public, and frontend/dist
"""

import os
import shutil
import wave
import struct
import math
import subprocess
import cv2
import numpy as np

FFMPEG_BIN = os.path.abspath("bin/ffmpeg")
if not os.path.exists(FFMPEG_BIN):
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

SEGMENTS_DEF = [
    {
        "segment_id": "ohms_law_master_lesson_001_intro",
        "title": "Welcome & Electric Potential",
        "pose_image": "assets/teacher/teacher_open_hands.jpg",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_001_intro.wav",
        "mouth_anchor": (523, 331),
        "eyes": [(488, 270), (558, 262)],
        "eyelid_color": (55, 70, 95),
        "whiteboard": "intro"
    },
    {
        "segment_id": "ohms_law_master_lesson_002_resistance",
        "title": "Understanding Electrical Resistance",
        "pose_image": "assets/teacher/male_professor_reference.png",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_002_resistance.wav",
        "mouth_anchor": (519, 361),
        "eyes": [(484, 270), (554, 262)],
        "eyelid_color": (52, 68, 92),
        "whiteboard": "resistance"
    },
    {
        "segment_id": "ohms_law_master_lesson_003_formula",
        "title": "The Fundamental Relationship: I = V / R",
        "pose_image": "assets/teacher/teacher_point.jpg",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_003_formula.wav",
        "mouth_anchor": (424, 362),
        "eyes": [(390, 310), (458, 305)],
        "eyelid_color": (50, 65, 88),
        "whiteboard": "formula"
    },
    {
        "segment_id": "ohms_law_master_lesson_004_example",
        "title": "Worked Numerical Example",
        "pose_image": "assets/teacher/teacher_point.jpg",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_004_example.wav",
        "mouth_anchor": (424, 362),
        "eyes": [(390, 310), (458, 305)],
        "eyelid_color": (50, 65, 88),
        "whiteboard": "calculation"
    },
    {
        "segment_id": "ohms_law_master_lesson_005_question",
        "title": "Diagnostic Checkpoint Question",
        "pose_image": "assets/teacher/teacher_open_hands.jpg",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_005_question.wav",
        "mouth_anchor": (523, 331),
        "eyes": [(488, 270), (558, 262)],
        "eyelid_color": (55, 70, 95),
        "whiteboard": "question"
    },
    {
        "segment_id": "ohms_law_master_lesson_006_doubt_response",
        "title": "Response to Student Doubt",
        "pose_image": "assets/teacher/male_professor_reference.png",
        "wav_file": "app/static/teacher/segments/ohms_law_master_lesson_006_doubt_response.wav",
        "mouth_anchor": (519, 361),
        "eyes": [(484, 270), (554, 262)],
        "eyelid_color": (52, 68, 92),
        "whiteboard": "doubt_response"
    }
]

def extract_envelopes(wav_path: str, fps: int, total_frames: int):
    with wave.open(wav_path, 'rb') as w:
        sr = w.getframerate()
        nframes = w.getnframes()
        raw = w.readframes(nframes)
    
    samples = struct.unpack(f"{len(raw)//2}h", raw)
    samples_per_frame = int(sr / float(fps))
    envelopes = []
    
    for f in range(total_frames):
        start = f * samples_per_frame
        end = min(len(samples), start + samples_per_frame)
        if start >= len(samples) or start == end:
            envelopes.append(0.0)
            continue
        chunk = samples[start:end]
        rms = math.sqrt(sum((s / 32768.0) ** 2 for s in chunk) / len(chunk))
        envelopes.append(min(1.0, rms * 4.5))
        
    smoothed = []
    for i in range(len(envelopes)):
        win = envelopes[max(0, i - 1):min(len(envelopes), i + 2)]
        smoothed.append(sum(win) / len(win))
    return smoothed

def generate_segment_video(seg_info: dict, fps: int = 24):
    seg_id = seg_info["segment_id"]
    wav_path = seg_info["wav_file"]
    pose_img_path = seg_info["pose_image"]
    mx, my = seg_info["mouth_anchor"]
    eyes = seg_info["eyes"]
    eyelid_color = seg_info["eyelid_color"]
    
    with wave.open(wav_path, 'rb') as w:
        sr = w.getframerate()
        nframes = w.getnframes()
        dur = nframes / float(sr)
        total_frames = int(dur * fps)
        
    envelopes = extract_envelopes(wav_path, fps, total_frames)
    
    base_img = cv2.imread(pose_img_path)
    if base_img is None:
        raise FileNotFoundError(f"Base image not found: {pose_img_path}")
    h, w = base_img.shape[:2]
    center = (w // 2, h // 2)
    
    temp_output = f"data/media/teacher/temp_{seg_id}.mp4"
    os.makedirs("data/media/teacher", exist_ok=True)
    
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{w}x{h}", "-pix_fmt", "bgr24", "-r", str(fps),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(sr),
        "-shortest",
        "-movflags", "+faststart",
        temp_output
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for f in range(total_frames):
        t = f / float(fps)
        
        # 1. Subtle breathing oscillation
        breath = 1.0 + 0.002 * math.sin(2 * math.pi * 0.25 * t)
        sway = 0.4 * math.sin(2 * math.pi * 0.35 * t)
        
        M = cv2.getRotationMatrix2D(center, sway, breath)
        M[1, 2] += 2.0 * math.sin(2 * math.pi * 0.25 * t)
        frame = cv2.warpAffine(base_img, M, (w, h), borderMode=cv2.BORDER_REFLECT_101)
        
        # 2. Eye blinking cycle
        blink_cycle = t % 3.5
        if 0.0 <= blink_cycle <= 0.22:
            bp = math.sin((blink_cycle / 0.22) * math.pi)
            eh = int(7 * (1.0 - bp * 0.85))
            for ex, ey in eyes:
                cv2.ellipse(frame, (ex, ey), (16, max(2, eh)), int(sway), 0, 360, eyelid_color, -1)
                
        # 3. Audio-synchronized mouth movement
        energy = envelopes[f] if f < len(envelopes) else 0.0
        if energy > 0.04:
            open_h = int(12 * energy)
            open_w = int(22 + 8 * (energy ** 0.5))
            overlay = frame.copy()
            # Oral cavity
            cv2.ellipse(overlay, (mx, my), (open_w, open_h), int(sway), 0, 360, (25, 30, 45), -1)
            # Upper teeth highlight
            if open_h >= 5:
                cv2.ellipse(overlay, (mx, my - open_h // 3), (int(open_w * 0.65), max(2, open_h // 4)), int(sway), 0, 180, (205, 210, 215), -1)
            # Soft lip border
            cv2.ellipse(overlay, (mx, my), (open_w + 2, open_h + 2), int(sway), 0, 360, (70, 85, 125), 1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f"FFmpeg failed with returncode {proc.returncode}: {err}")
        
    # Distribute to destinations
    dests = [
        f"data/media/teacher/segments/{seg_id}.mp4",
        f"app/static/teacher/segments/{seg_id}.mp4",
        f"frontend/public/teacher/segments/{seg_id}.mp4",
        f"frontend/dist/teacher/segments/{seg_id}.mp4"
    ]
    for d in dests:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(temp_output, d)
        
    os.remove(temp_output)
    print(f"Successfully generated {seg_id}.mp4 ({dur:.2f}s, {total_frames} frames) with H.264 + AAC audio!")

def main():
    print("=== Generating 6 Master Teacher Video Segments with Audio & Gestures ===")
    for s in SEGMENTS_DEF:
        generate_segment_video(s)
    print("=== All 6 Segments Generated & Distributed Successfully! ===")

if __name__ == "__main__":
    main()

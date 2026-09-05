"""
High-Quality Prototype Teacher Video Generator.
Produces professional, artifact-free 16:9 1280x720 MP4 clips:
- 100% photographic texture (NO painted ellipses, NO cartoon patches)
- Real speech articulation via jaw/lip sub-pixel remap driven by audio RMS
- Realistic eyelid blinks via skin fold displacement
- Natural camera pedestal tracking, subtle collegiate sway, and speech emphasis nodding
- H.264 video + AAC 192k audio with +faststart
"""

import os
import wave
import struct
import math
import subprocess
import cv2
import numpy as np
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

# Load high-resolution poses
img_open = cv2.imread("assets/teacher/teacher_open_hands.jpg")
img_point = cv2.imread("assets/teacher/teacher_point.jpg")
img_rest = cv2.imread("assets/teacher/male_professor_reference.png")

CANVAS_W, CANVAS_H = 1280, 720
FG_SIZE = 720
X_OFF = (CANVAS_W - FG_SIZE) // 2

def create_base_canvas(source_img):
    canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
    bg = cv2.resize(source_img, (CANVAS_W, CANVAS_H))
    bg_blur = cv2.GaussianBlur(bg, (45, 45), 0)
    bg_blur = (bg_blur * 0.45).astype(np.uint8)

    fg = cv2.resize(source_img, (FG_SIZE, FG_SIZE))
    canvas[:] = bg_blur
    canvas[:, X_OFF:X_OFF + FG_SIZE] = fg

    # Soft drop shadow at borders
    for i in range(25):
        alpha = i / 25.0
        canvas[:, X_OFF - 25 + i] = (canvas[:, X_OFF - 25 + i] * alpha).astype(np.uint8)
        canvas[:, X_OFF + FG_SIZE + 25 - i - 1] = (canvas[:, X_OFF + FG_SIZE + 25 - i - 1] * alpha).astype(np.uint8)

    return canvas

# Pre-render 16:9 base canvases
canvas_open = create_base_canvas(img_open)
canvas_point = create_base_canvas(img_point)
canvas_rest = create_base_canvas(img_rest)

# Landmarks on 1280x720 canvas
# Open / Rest poses (face centered around x = 280 + 368 = 648, y = 200)
OPEN_MX, OPEN_MY = 648, 230
OPEN_EYES = [(622, 184), (676, 184)]

# Point pose (face centered around x = 280 + 296 = 576, y = 227)
POINT_MX, POINT_MY = 576, 252
POINT_EYES = [(552, 218), (598, 215)]

CLIPS = [
    {
        "names": ["ohms_law_master_lesson_001_intro", "male_intro"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_001_intro.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["ohms_law_master_lesson_002_resistance", "male_explain"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_002_resistance.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["ohms_law_master_lesson_003_formula", "male_point"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_003_formula.wav",
        "canvas": canvas_point, "mx": POINT_MX, "my": POINT_MY, "eyes": POINT_EYES,
        "is_point": True
    },
    {
        "names": ["ohms_law_master_lesson_004_example", "male_example"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_004_example.wav",
        "canvas": canvas_point, "mx": POINT_MX, "my": POINT_MY, "eyes": POINT_EYES,
        "is_point": True
    },
    {
        "names": ["ohms_law_master_lesson_005_question", "male_question"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_005_question.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["ohms_law_master_lesson_006_doubt_response"],
        "wav": "app/static/teacher/segments/ohms_law_master_lesson_006_doubt_response.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["male_think"],
        "wav": "app/static/teacher/segments/male_think.wav",
        "canvas": canvas_rest, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["male_correct"],
        "wav": "app/static/teacher/segments/male_correct.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["male_encourage"],
        "wav": "app/static/teacher/segments/male_encourage.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    },
    {
        "names": ["male_celebrate"],
        "wav": "app/static/teacher/segments/male_celebrate.wav",
        "canvas": canvas_open, "mx": OPEN_MX, "my": OPEN_MY, "eyes": OPEN_EYES,
        "is_point": False
    }
]

def extract_audio_rms(wav_path, fps, total_frames):
    with wave.open(wav_path, 'rb') as wf:
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    samples = struct.unpack(f"{len(raw)//2}h", raw)
    spf = int(sr / fps)
    rms_list = []
    for f in range(total_frames):
        st = f * spf
        en = min(len(samples), st + spf)
        if st >= len(samples) or st == en:
            rms_list.append(0.0)
            continue
        chunk = samples[st:en]
        val = math.sqrt(sum((s / 32768.0) ** 2 for s in chunk) / len(chunk))
        rms_list.append(min(1.0, val * 4.0))

    # 3-frame moving average for natural smoothing
    smooth = []
    for i in range(len(rms_list)):
        win = rms_list[max(0, i-1):min(len(rms_list), i+2)]
        smooth.append(sum(win) / len(win))
    return smooth, sr

def render_clip(clip_def, fps=24):
    wav_path = clip_def["wav"]
    primary_name = clip_def["names"][0]
    base_canvas = clip_def["canvas"]
    mx, my = clip_def["mx"], clip_def["my"]
    eyes = clip_def["eyes"]
    is_point = clip_def["is_point"]

    with wave.open(wav_path, 'rb') as wf:
        sr = wf.getframerate()
        nframes = wf.getnframes()
        dur = nframes / float(sr)
        total_frames = int(dur * fps)

    rms_profile, _ = extract_audio_rms(wav_path, fps, total_frames)

    temp_out = f"data/media/teacher/temp_{primary_name}.mp4"
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{CANVAS_W}x{CANVAS_H}", "-pix_fmt", "bgr24", "-r", str(fps),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(sr),
        "-shortest", "-movflags", "+faststart",
        temp_out
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    y_grid, x_grid = np.indices((CANVAS_H, CANVAS_W), dtype=np.float32)

    center = (CANVAS_W // 2, CANVAS_H // 2)

    for f in range(total_frames):
        t = f / float(fps)
        energy = rms_profile[f] if f < len(rms_profile) else 0.0

        # 1. Subtle camera pedestal push-in & cinematic floating sway
        cam_scale = 1.0 + 0.015 * (t / max(1.0, dur))
        cam_dx = 3.0 * math.sin(0.35 * t)
        cam_dy = 2.0 * math.cos(0.25 * t) + 1.5 * math.sin(2 * math.pi * 0.22 * t)  # Breathing

        # Emphatic head nod when speaking emphatically
        nod = 2.5 * max(0.0, energy - 0.35)
        cam_dy += nod

        # Subtle collegiate tilt
        tilt = -0.6 if is_point else 0.4 * math.sin(2 * math.pi * 0.15 * t)

        M = cv2.getRotationMatrix2D(center, tilt, cam_scale)
        M[0, 2] += cam_dx
        M[1, 2] += cam_dy

        frame = cv2.warpAffine(base_canvas, M, (CANVAS_W, CANVAS_H), borderMode=cv2.BORDER_REFLECT_101)

        # Track landmark positions through affine transformation
        pt_m = M @ np.array([mx, my, 1.0])
        cur_mx, cur_my = pt_m[0], pt_m[1]

        cur_eyes = []
        for ex, ey in eyes:
            pt_e = M @ np.array([ex, ey, 1.0])
            cur_eyes.append((pt_e[0], pt_e[1]))

        # 2. Photorealistic Speech Articulation (Lower lip/jaw remap only - NO shapes!)
        jaw_drop = 8.5 * energy
        map_y = y_grid.copy()
        if jaw_drop > 0.8:
            dx = (x_grid - cur_mx) / 28.0
            dy_lower = (y_grid - (cur_my + 10)) / 24.0
            r2_lower = dx**2 + dy_lower**2
            warp_lower = jaw_drop * np.exp(-r2_lower) * (y_grid >= (cur_my - 2))
            map_y -= warp_lower

            dy_upper = (y_grid - (cur_my - 6)) / 10.0
            r2_upper = dx**2 + dy_upper**2
            warp_upper = (jaw_drop * 0.25) * np.exp(-r2_upper) * (y_grid < (cur_my - 2))
            map_y += warp_upper

        # 3. Photorealistic Eye Blink (Skin fold descent only - NO shapes!)
        blink_cycle = t % 3.4
        if 0.0 <= blink_cycle <= 0.20:
            bp = math.sin((blink_cycle / 0.20) * math.pi)
            for ex, ey in cur_eyes:
                dx = (x_grid - ex) / 14.0
                dy = (y_grid - (ey - 2)) / 8.0
                r2 = dx**2 + dy**2
                warp_lid = (bp * 6.5) * np.exp(-r2) * (y_grid < (ey + 6))
                map_y -= warp_lid

        if jaw_drop > 0.8 or (0.0 <= blink_cycle <= 0.20):
            frame = cv2.remap(frame, x_grid, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()

    # Distribute to all static directories
    dest_dirs = [
        "app/static/teacher/segments",
        "frontend/dist/teacher/segments",
        "frontend/public/teacher/segments",
        "data/media/teacher/segments"
    ]
    for d in dest_dirs:
        os.makedirs(d, exist_ok=True)
        for name in clip_def["names"]:
            target = os.path.join(d, f"{name}.mp4")
            subprocess.run(["cp", temp_out, target], check=True)

    print(f"✓ Rendered {primary_name}.mp4 ({dur:.2f}s, {total_frames} frames)")

# Also create teacher_video_audio_test.mp4
def render_audio_test():
    # Use ohms_law_master_lesson_001_intro as test sound
    src = "app/static/teacher/segments/ohms_law_master_lesson_001_intro.mp4"
    for dest in [
        "app/static/teacher/teacher_video_audio_test.mp4",
        "frontend/dist/teacher/teacher_video_audio_test.mp4",
        "frontend/public/teacher/teacher_video_audio_test.mp4"
    ]:
        subprocess.run(["cp", src, dest], check=True)
    print("✓ Created teacher_video_audio_test.mp4")

if __name__ == "__main__":
    print("Starting generation of 10 high-quality teacher clips...")
    for c in CLIPS:
        render_clip(c)
    render_audio_test()
    print("ALL 10 CLIPS SUCCESSFULLY GENERATED!")

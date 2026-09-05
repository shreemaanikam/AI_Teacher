# Teacher Media Pipeline Licenses & Model Attributions

This document provides comprehensive licensing, attribution, and architecture disclosures for the **Photorealistic Adult Male AI Teacher Video & Audio Pipeline** in **Apurva AI Teacher**.

---

## 1. Teacher Persona Attribution

- **Teacher Identity**: Prof. Richard Davies, Ph.D.
- **Role**: College Professor, Department of Applied Physics & Engineering
- **Visual Appearance**: Fictional adult male professor (mid 40s), navy blazer, spectacles, professorial demeanor.
- **Reference Image**: `data/media/teacher/male_professor_01.jpg` (and distributed to `app/static/teacher/`, `frontend/public/teacher/`, `frontend/dist/teacher/`).
- **Asset License**: Created and licensed for Apurva AI Teacher under MIT License and Permissive Educational Hackathon Use.

---

## 2. Text-to-Speech (TTS) Frameworks

### Primary Generative: Kokoro ONNX
- **Project**: [Kokoro-82M / kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)
- **License**: Apache License 2.0
- **Voices**: `am_michael` (American Male Academic), `bm_george` (British Male Academic)
- **Usage**: Offline, CPU-accelerated neural text-to-speech with sub-200ms latency.

### Secondary Generative: Bark (Suno)
- **Project**: [Suno Bark](https://github.com/suno-ai/bark)
- **License**: MIT License
- **Usage**: Deep expressive speech synthesis with realistic breaths, laughter, and hesitation cues for lecture transitions.

### Operating System Native: macOS / Apple Speech Synthesis
- **Component**: `/usr/bin/say` with high-definition educational male voice (`Daniel`)
- **License**: Built-in Apple Darwin System Utility (macOS Developer Agreement)
- **Sample Rate**: 24,000 Hz, 16-bit Linear PCM WAV
- **Usage**: Zero-dependency, ultra-reliable studio-grade audio synthesis on Apple Silicon / Darwin host machines.

### Pure Python Procedural: Formant Harmonic Vocoder
- **Component**: `backend/services/teacher_media/tts/procedural_provider.py`
- **License**: MIT License (Original work in this repository)
- **Usage**: Deterministic zero-dependency pure Python formant filter bank synthesis (F1 500Hz, F2 1500Hz, F3 2500Hz) ensuring the application can synthesize speech anywhere.

---

## 3. Lip Synchronization & Video Synthesis

### Deep Learning Lip Sync: MuseTalk
- **Project**: [TMElyralab / MuseTalk](https://github.com/TMElyralab/MuseTalk)
- **License**: MIT License / Academic Permissive Use
- **Usage**: Real-time audio-driven talking face generation based on latent diffusion. Gracefully disabled on environments without CUDA / pre-downloaded weights.

### Deep Learning Face Animation: LivePortrait
- **Project**: [KwaiVGI / LivePortrait](https://github.com/KwaiVGI/LivePortrait)
- **License**: MIT License / Open-Source Academic
- **Usage**: Stitching and retargeting facial dynamics from reference video drivers (`Real_AI_Teacher.mp4`) onto the professor portrait.

### Deterministic Procedural Lip Sync & Facial Easing: Viseme LipSync
- **Component**: `backend/services/teacher_media/avatar/procedural_avatar.py` & `lipsync/viseme_lipsync.py`
- **License**: MIT License (Original work in this repository)
- **Usage**: OpenCV-based frame compositor using natural Poisson blinking intervals, organic head sway, respiratory chest motion, and RMS audio energy viseme aperture modulation.

---

## 4. Media Processing & Container Libraries

### FFmpeg
- **Project**: [FFmpeg](https://ffmpeg.org/)
- **License**: LGPL v2.1+ / GPL v2+
- **Usage**: Audio-video muxing, H.264/AAC transcoding, and container validation. Used strictly as an external subprocess with safe parameter arrays.

### OpenCV (Open Source Computer Vision Library)
- **Project**: [OpenCV](https://opencv.org/)
- **License**: Apache License 2.0
- **Usage**: Frame rendering, image blending, facial contour drawing, and H.264 video encoding via `cv2.VideoWriter`.

### NumPy
- **Project**: [NumPy](https://numpy.org/)
- **License**: BSD 3-Clause License
- **Usage**: Multidimensional matrix manipulation and signal processing for audio envelopes.

---

## 5. Pre-Generated Demonstration Lesson Assets

The 6 canonical Physics Ohm's Law lesson video segments:
1. `ohms_law_master_lesson_001_intro.mp4` (6.17s)
2. `ohms_law_master_lesson_002_resistance.mp4` (7.58s)
3. `ohms_law_master_lesson_003_formula.mp4` (7.75s)
4. `ohms_law_master_lesson_004_example.mp4` (7.67s)
5. `ohms_law_master_lesson_005_question.mp4` (7.42s)
6. `ohms_law_master_lesson_006_doubt_response.mp4` (9.00s)

were created directly using this pipeline and are distributed within the repository under the **MIT License** for live hackathon evaluation and demonstrations.

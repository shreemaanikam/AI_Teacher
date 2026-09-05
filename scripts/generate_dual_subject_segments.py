#!/usr/bin/env python3
"""
Dual-Subject Segment Media Generator.
Synthesizes concept explanation video and audio clips across Physics (Ohm's Law)
and Machine Learning (Gradient Descent) using the canonical male AI teacher video and voice.
"""

import os
import sys
import shutil
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.teacher_media.voice import generate_teacher_voice
from backend.services.teacher_media.avatar import generate_teacher_video

CANONICAL_TEACHER = "public/teacher-avatar/male_teacher.mp4"

PHYSICS_SEGMENTS = [
    {
        "id": "seg_01_intro",
        "title": "Welcome & Electric Potential",
        "teacher_state": "INTRODUCING",
        "teacher_action": "introducing",
        "script": "Good morning class. Today we will explore Ohm's Law, which forms the cornerstone of circuit theory."
    },
    {
        "id": "seg_02_voltage",
        "title": "Understanding Voltage (Potential Difference)",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "Voltage, or electric potential difference, is the electrical pressure from a power source that pushes electrons through a conducting loop."
    },
    {
        "id": "seg_03_current",
        "title": "Understanding Current (Flow of Charge)",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "Current is the rate at which electric charge flows past a point in a circuit, measured in amperes, where one ampere equals one coulomb per second."
    },
    {
        "id": "seg_04_resistance",
        "title": "Understanding Electrical Resistance",
        "teacher_state": "EXPLAINING",
        "teacher_action": "point_to_formula",
        "script": "Resistance is the opposition to the flow of electrical charge. When electrons drift through a conductor, they collide with lattice ions."
    },
    {
        "id": "seg_05_formula",
        "title": "The Master Equation: I = V / R",
        "teacher_state": "POINTING",
        "teacher_action": "point_to_formula",
        "script": "Using Ohm's Law, the current I in amperes equals voltage V divided by resistance R. Notice the direct proportionality to voltage and inverse relationship with resistance."
    },
    {
        "id": "seg_06_example",
        "title": "Worked Numerical Circuit Example",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "For example, if our battery supplies nine volts across a three ohm resistor, the resulting current is exactly three amperes."
    }
]

ML_SEGMENTS = [
    {
        "id": "seg_01_intro",
        "title": "Welcome & Optimization Foundations",
        "teacher_state": "INTRODUCING",
        "teacher_action": "introducing",
        "script": "Welcome back. Today we examine Gradient Descent, the foundational first-order optimization algorithm that powers modern machine learning."
    },
    {
        "id": "seg_02_loss_surface",
        "title": "The Objective & Loss Surface J(w)",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "Our objective is to minimize a loss function J of theta, which measures the difference between model predictions and true ground truth targets across parameter space."
    },
    {
        "id": "seg_03_learning_rate",
        "title": "Learning Rate (Step Size Alpha)",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "The learning rate alpha controls our step size. If alpha is too small, convergence takes forever; if too large, the updates will oscillate or diverge."
    },
    {
        "id": "seg_04_gradient_direction",
        "title": "Gradient Vector & Steepest Descent",
        "teacher_state": "POINTING",
        "teacher_action": "point_to_formula",
        "script": "The gradient vector points in the direction of steepest ascent on the loss surface. Therefore, to minimize error, we take steps in the negative gradient direction."
    },
    {
        "id": "seg_05_update_rule",
        "title": "Parameter Update Rule: w_t+1 = w_t - alpha * grad",
        "teacher_state": "POINTING",
        "teacher_action": "point_to_formula",
        "script": "Here is the master parameter update equation: theta at t plus one equals theta at t minus alpha times the gradient of the loss function."
    },
    {
        "id": "seg_06_example",
        "title": "Model Training & Convergence Example",
        "teacher_state": "EXPLAINING",
        "teacher_action": "explain_example",
        "script": "In training deep neural networks and linear models, repeated mini-batch gradient descent iteratively drives weights toward the global or local minimum."
    }
]


def generate_subject(subject_key: str, segments: list):
    print(f"\n==================================================")
    print(f"🎬 Generating Concept Segments for: {subject_key.upper()}")
    print(f"==================================================")

    out_dir = PROJECT_ROOT / "public" / "teacher-avatar" / "generated" / subject_key
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for i, seg in enumerate(segments, 1):
        seg_id = seg["id"]
        title = seg["title"]
        script = seg["script"]
        action = seg["teacher_action"]
        state = seg["teacher_state"]

        wav_path = str(out_dir / f"{seg_id}.wav")
        mp4_path = str(out_dir / f"{seg_id}.mp4")

        print(f"\n[{i}/{len(segments)}] {seg_id}: {title}")
        print(f"  📝 Script: \"{script[:60]}...\"")
        print(f"  🎯 Action: {action} | State: {state}")

        # 1. Generate Voice
        print(f"  🔊 Synthesizing male teacher voice...")
        voice_res = generate_teacher_voice(
            script=script,
            voice_reference=CANONICAL_TEACHER,
            output_path=wav_path
        )
        print(f"     -> Audio: {voice_res['duration']}s, provider={voice_res['provider']}")

        # 2. Generate Video with Lip Sync and Action Steering
        print(f"  🎥 Generating teacher video with speech lip-sync...")
        video_res = generate_teacher_video(
            source_teacher=CANONICAL_TEACHER,
            audio=wav_path,
            teacher_state=state,
            output_path=mp4_path,
            teacher_action=action
        )
        print(f"     -> Video: {video_res['duration']}s, saved to {mp4_path}")

        results.append({
            "id": seg_id,
            "title": title,
            "teacher_state": state,
            "teacher_action": action,
            "duration": video_res["duration"],
            "video_path": str(Path(mp4_path).relative_to(PROJECT_ROOT)),
            "audio_path": str(Path(wav_path).relative_to(PROJECT_ROOT)),
            "script": script
        })

    # Save manifest
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump({"subject": subject_key, "count": len(results), "segments": results}, f, indent=2)
    print(f"\n✅ Manifest saved to {manifest_path}")

    # Mirror to app/static and frontend/public
    static_dest = PROJECT_ROOT / "app" / "static" / "teacher-avatar" / "generated" / subject_key
    frontend_dest = PROJECT_ROOT / "frontend" / "public" / "teacher-avatar" / "generated" / subject_key
    
    for dest in [static_dest, frontend_dest]:
        dest.mkdir(parents=True, exist_ok=True)
        for item in out_dir.iterdir():
            shutil.copy2(item, dest / item.name)
        print(f"  🔄 Mirrored to {dest}")

    return results


def main():
    if not (PROJECT_ROOT / CANONICAL_TEACHER).exists():
        print(f"❌ Canonical teacher video not found at {CANONICAL_TEACHER}")
        sys.exit(1)

    print(f"Found canonical teacher video at {CANONICAL_TEACHER}")

    physics_res = generate_subject("physics", PHYSICS_SEGMENTS)
    ml_res = generate_subject("machine-learning", ML_SEGMENTS)

    print("\n==================================================")
    print("🎉 ALL DUAL-SUBJECT SEGMENTS SUCCESSFULLY GENERATED!")
    print(f"Physics: {len(physics_res)} clips")
    print(f"Machine Learning: {len(ml_res)} clips")
    print("==================================================")


if __name__ == "__main__":
    main()

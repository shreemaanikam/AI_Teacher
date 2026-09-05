"""
Teacher Avatar Video Generation Service.
Connects the canonical adult male teacher video with concept speech and pedagogical actions.
"""

import os
from typing import Optional, Dict, Any
from backend.services.teacher_media.lipsync import synchronize_lips


def generate_teacher_video(
    source_teacher: str,
    audio: str,
    teacher_state: str = "EXPLAINING",
    output_path: Optional[str] = None,
    teacher_action: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates concept explanation video matching teacher state and action.
    """
    if not output_path:
        import uuid
        output_path = f"data/media/teacher/cache/avatar_{uuid.uuid4().hex[:8]}.mp4"

    res = synchronize_lips(
        teacher_video=source_teacher,
        teacher_audio=audio,
        output_path=output_path,
        teacher_action=teacher_action,
        teacher_state=teacher_state
    )

    return {
        "video_path": res["final_video"],
        "duration": res["duration"],
        "metadata": {
            **res["metadata"],
            "teacher_state": teacher_state,
            "teacher_action": teacher_action,
            "source_teacher": source_teacher
        }
    }

"""
Teacher Video Composition Engine.
Assembles animated male professor frames, audio synchronization, and visual whiteboard cues.
Outputs browser-playable MP4 video.
"""

import os
import shutil
from typing import List, Optional
import cv2
import numpy as np
from pydantic import BaseModel

from .validation import validate_video
from .ffmpeg import FFmpegExecutor
from ..profile import TeacherState


class VideoMetadata(BaseModel):
    video_path: str
    audio_path: Optional[str] = None
    duration_seconds: float
    width: int
    height: int
    fps: int
    is_valid: bool
    codec: str
    teacher_state: TeacherState


class VideoComposer:
    def __init__(self):
        self.ffmpeg = FFmpegExecutor()

    def compose_video(
        self,
        frames: List[np.ndarray],
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        fps: int = 24,
        teacher_state: TeacherState = TeacherState.EXPLAINING
    ) -> VideoMetadata:
        if not frames:
            raise ValueError("Cannot compose video from empty frame list.")
            
        h, w, _ = frames[0].shape
        if not output_path:
            import uuid
            output_path = f"data/media/teacher/cache/teacher_vid_{uuid.uuid4().hex[:8]}.mp4"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write frames via OpenCV using browser-playable avc1 (H.264)
        raw_video_path = output_path if not self.ffmpeg.is_available() or not audio_path else output_path + ".raw.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(raw_video_path, fourcc, float(fps), (w, h))
        if not out.isOpened():
            # Fallback to mp4v if avc1 fails
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(raw_video_path, fourcc, float(fps), (w, h))
            
        for frame in frames:
            out.write(frame)
        out.release()
        
        # If FFmpeg is available and audio is present, mux audio into MP4
        final_video_path = raw_video_path
        if self.ffmpeg.is_available() and audio_path and os.path.exists(audio_path):
            muxed_ok = self.ffmpeg.mux_video_audio(raw_video_path, audio_path, output_path)
            if muxed_ok:
                final_video_path = output_path
                if os.path.exists(raw_video_path) and raw_video_path != output_path:
                    os.remove(raw_video_path)
                    
        duration = round(len(frames) / float(fps), 2)
        is_ok = validate_video(final_video_path)
        
        return VideoMetadata(
            video_path=final_video_path,
            audio_path=audio_path,
            duration_seconds=duration,
            width=w,
            height=h,
            fps=fps,
            is_valid=is_ok,
            codec="H.264/avc1",
            teacher_state=teacher_state
        )

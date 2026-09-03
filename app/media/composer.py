"""
Video Composer and Media Timeline Assembler for Module 9 (Voice + Avatar + Video Engine).
Synchronizes narration audio, avatar presenter, visual assets, and timed captions into cohesive teaching segments.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timezone

from app.media.models import (
    MediaSegment,
    MediaStatus,
    TeachingScript,
    AudioAsset,
    AvatarAsset,
    CaptionAsset,
    TimedCaptionCue,
)
from app.visuals.models import VisualAsset

import shutil
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)


class VideoComposer:
    """
    Assembles multimodal assets into a synchronized teaching segment.
    Enforces the core reliability invariant: media failures degrade gracefully
    and never destroy pedagogical progress or crash the lesson session.
    Supports real MP4 rendering via FFmpeg when available.
    """

    def is_ffmpeg_available(self) -> bool:
        """Checks if ffmpeg binary is present on the host system."""
        return shutil.which("ffmpeg") is not None

    def render_mp4_video(
        self,
        segment_id: str,
        audio: Optional[AudioAsset],
        visual_asset: Optional[VisualAsset],
        duration: float,
    ) -> Optional[str]:
        """
        Synthesizes a real playable H.264/AAC MP4 video if ffmpeg is available.
        Returns the absolute filepath to the MP4 file or None if ffmpeg is unavailable.
        """
        if not self.is_ffmpeg_available() or not audio:
            return None

        try:
            out_dir = os.path.join(os.getcwd(), "data", "videos")
            os.makedirs(out_dir, exist_ok=True)
            mp4_path = os.path.join(out_dir, f"{segment_id}.mp4")

            # Extract audio bytes from data URI
            if audio.content_uri.startswith("data:audio/wav;base64,"):
                import base64
                b64_data = audio.content_uri.split(",", 1)[1]
                wav_bytes = base64.b64decode(b64_data)
            else:
                return None

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                wav_file.write(wav_bytes)
                wav_path = wav_file.name

            try:
                # Use FFmpeg testsrc / lavfi color canvas combined with audio to produce real valid MP4
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=0x0f172a:s=1280x720:d={duration}",
                    "-i", wav_path,
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    mp4_path,
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                if result.returncode == 0 and os.path.exists(mp4_path):
                    logger.info(f"Successfully compiled real MP4 video to: {mp4_path}")
                    return mp4_path
                else:
                    logger.warning(f"FFmpeg compilation returned non-zero code: {result.stderr.decode('utf-8', errors='ignore')[:200]}")
                    return None
            finally:
                if os.path.exists(wav_path):
                    os.remove(wav_path)

        except Exception as e:
            logger.warning(f"Failed to generate MP4 with FFmpeg: {e}. Falling back to interactive manifest.")
            return None

    def generate_captions(self, script: TeachingScript, total_duration: float) -> CaptionAsset:
        """Splits spoken text into timed subtitle cues and builds WebVTT content."""
        sentences = [s.strip() for s in script.spoken_script.replace("।", ".").split(".") if s.strip()]
        if not sentences:
            sentences = [script.spoken_script]

        chunk_dur = total_duration / len(sentences)
        cues: List[TimedCaptionCue] = []
        vtt_lines = ["WEBVTT", ""]

        for idx, sentence in enumerate(sentences):
            start = round(idx * chunk_dur, 2)
            end = round((idx + 1) * chunk_dur, 2)
            cues.append(TimedCaptionCue(start_seconds=start, end_seconds=end, text=sentence))

            # Format 00:00.000 -> 00:00.000
            m_s, s_s = divmod(start, 60)
            m_e, s_e = divmod(end, 60)
            vtt_lines.append(f"{idx + 1}")
            vtt_lines.append(f"{int(m_s):02d}:{s_s:06.3f} --> {int(m_e):02d}:{s_e:06.3f}")
            vtt_lines.append(sentence)
            vtt_lines.append("")

        return CaptionAsset(
            language=script.language,
            vtt_content="\n".join(vtt_lines),
            cues=cues,
        )

    def assemble_segment(
        self,
        lesson_id: str,
        script: TeachingScript,
        audio: Optional[AudioAsset] = None,
        avatar: Optional[AvatarAsset] = None,
        visual_asset: Optional[VisualAsset] = None,
        session_id: Optional[str] = None,
    ) -> MediaSegment:
        """
        Synthesizes a complete MediaSegment from available components with multi-tier fallback.
        """
        duration = audio.duration_seconds if audio else script.estimated_duration_seconds
        captions = self.generate_captions(script, duration)

        is_fallback = False
        error_msg = None

        if not audio and not avatar:
            is_fallback = True
            error_msg = "Audio and avatar unavailable; operating in caption+visual fallback mode."
        elif not avatar:
            is_fallback = True
            error_msg = "Avatar unavailable; operating in voice+visual fallback mode."

        status = MediaStatus.FALLBACK if is_fallback else MediaStatus.READY

        # Attempt real MP4 compilation if FFmpeg is available
        segment_id = f"seg_{uuid.uuid4().hex[:12]}"
        mp4_path = self.render_mp4_video(segment_id, audio, visual_asset, duration)

        # Construct responsive playback manifest for frontend / HTML player
        playback_manifest = {
            "version": "1.0",
            "duration": duration,
            "language": script.language,
            "concept": script.concept,
            "strategy": script.teaching_strategy.value,
            "audio_track": audio.content_uri if audio else None,
            "avatar_track": avatar.content_uri if avatar else None,
            "visual_track": visual_asset.content if visual_asset else None,
            "visual_format": visual_asset.format.value if visual_asset else "none",
            "captions": captions.vtt_content,
            "on_screen_text": script.on_screen_text,
            "pause_points": script.pause_points,
            "question_points": script.question_points,
            "mp4_video_path": mp4_path,
            "has_mp4_video": mp4_path is not None,
        }

        return MediaSegment(
            lesson_id=lesson_id,
            session_id=session_id,
            concept=script.concept,
            teaching_strategy=script.teaching_strategy,
            language=script.language,
            status=status,
            duration_seconds=duration,
            script=script,
            audio=audio,
            avatar=avatar,
            visual_spec_id=visual_asset.spec_id if visual_asset else None,
            visual_asset_id=visual_asset.asset_id if visual_asset else None,
            captions=captions,
            video_url=mp4_path or (avatar.content_uri if avatar else (visual_asset.content if visual_asset else None)),
            playback_manifest=playback_manifest,
            is_fallback_mode=is_fallback,
            error_message=error_msg,
        )

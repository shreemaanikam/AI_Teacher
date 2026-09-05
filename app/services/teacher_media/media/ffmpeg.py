"""
Safe Subprocess FFmpeg Media Processing Engine.
Never executes raw unescaped shell strings. Uses strict argument arrays.
"""

import os
import re
import shutil
import subprocess
from typing import List, Dict, Any, Optional


def find_ffmpeg_binary() -> Optional[str]:
    """Finds a functional ffmpeg binary across common system and bundled paths."""
    candidates = [
        shutil.which("ffmpeg"),
        os.path.abspath("bin/ffmpeg"),
    ]
    try:
        import imageio_ffmpeg
        candidates.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        pass

    candidates.extend([
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ])

    for c in candidates:
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return os.path.abspath(c)
    return None


class FFmpegExecutor:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or find_ffmpeg_binary()

    def is_available(self) -> bool:
        return self.ffmpeg_path is not None and os.path.exists(self.ffmpeg_path)

    def mux_video_audio(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Muxes an H.264 video file and audio file into an MP4 container with faststart."""
        if not self.is_available():
            return False

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return True
            # Fallback to re-encoding video if stream copy fails
            cmd_reencode = [
                self.ffmpeg_path,
                "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            res2 = subprocess.run(cmd_reencode, capture_output=True, text=True, timeout=60)
            return res2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        except Exception:
            return False

    def create_video_with_audio(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
        fps: int = 24
    ) -> bool:
        """Creates a browser-playable H.264 MP4 with AAC audio from an image and WAV."""
        if not self.is_available() or not os.path.exists(image_path) or not os.path.exists(audio_path):
            return False

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        except Exception:
            return False

    def probe_media(self, file_path: str) -> Dict[str, Any]:
        """Probes video and audio streams of a media file."""
        res_data = {
            "audio_present": False,
            "video_present": False,
            "audio_duration": 0.0,
            "video_duration": 0.0,
            "codec": {},
            "sample_rate": 0,
            "channels": 0,
            "error": None
        }
        if not self.is_available():
            res_data["error"] = "FFmpeg binary not available"
            return res_data

        if not os.path.exists(file_path):
            res_data["error"] = f"File not found: {file_path}"
            return res_data

        try:
            cmd = [self.ffmpeg_path, "-i", file_path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            stderr = proc.stderr

            # Extract duration
            dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
            if dur_match:
                hours, minutes, seconds = dur_match.groups()
                total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                res_data["audio_duration"] = round(total_seconds, 2)
                res_data["video_duration"] = round(total_seconds, 2)

            # Check Video stream
            video_match = re.search(r"Stream #\d+:\d+.*Video:\s*([a-zA-Z0-9_\-]+)", stderr)
            if video_match:
                res_data["video_present"] = True
                res_data["codec"]["video"] = video_match.group(1)

            # Check Audio stream
            audio_match = re.search(r"Stream #\d+:\d+.*Audio:\s*([a-zA-Z0-9_\-]+).*?(\d+)\s*Hz.*?(\bmono\b|\bstereo\b|\b\d+\s*channels\b)", stderr)
            if audio_match:
                res_data["audio_present"] = True
                res_data["codec"]["audio"] = audio_match.group(1)
                res_data["sample_rate"] = int(audio_match.group(2))
                ch_str = audio_match.group(3).lower()
                res_data["channels"] = 1 if "mono" in ch_str else 2 if "stereo" in ch_str else 2

            return res_data
        except Exception as e:
            res_data["error"] = str(e)
            return res_data

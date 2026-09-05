"""
D-ID Avatar Video Provider for Module 9.
Integrates real D-ID Talks API adhering strictly to account credit limits with procedural SVG fallback.
"""

from __future__ import annotations
import os
import json
import logging
import time
import urllib.request
import urllib.error
from typing import Dict, List, Optional

from app.media.avatar.base import AvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.models import TeachingScript, AudioAsset, AvatarAsset

logger = logging.getLogger("DIDAvatarProvider")


class DIDAvatarProvider(AvatarProvider):
    """
    Production Video Presenter Provider connecting to D-ID Talks API.
    Maintains segment-level video rendering and automated procedural SVG fallback.
    """

    DEFAULT_SOURCE_URL = "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/image.jpeg"

    def __init__(self, api_key: Optional[str] = None):
        if api_key is not None:
            raw_key = api_key
        else:
            raw_key = os.getenv("DID_API_KEY") or ""
        self.api_key = raw_key.strip().strip("'\"")
        self.fallback = ProceduralAvatarProvider()


    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_supported_styles(self) -> List[str]:
        return ["academic_mentor", "female_teacher", "male_professor", "interactive_tutor"]

    def check_remaining_credits(self) -> int:
        if not self.is_configured():
            return 0
        try:
            url = "https://api.d-id.com/credits"
            headers = {"Authorization": f"Basic {self.api_key}", "accept": "application/json"}
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                credits_list = data.get("credits", [])
                if credits_list:
                    return int(credits_list[0].get("remaining", 0))
                return 0
        except Exception as e:
            logger.warning(f"Failed to check D-ID credits: {e}")
            return 0

    def generate_avatar(
        self,
        script: TeachingScript,
        audio: AudioAsset,
        presenter_style: str = "academic_mentor",
        visual_context: Optional[str] = None,
    ) -> AvatarAsset:
        if not self.is_configured():
            return self.fallback.generate_avatar(script, audio, presenter_style, visual_context)

        credits_left = self.check_remaining_credits()
        if credits_left <= 0:
            logger.info(f"D-ID credits exhausted ({credits_left}). Falling back to procedural presenter.")
            return self.fallback.generate_avatar(script, audio, presenter_style, visual_context)

        try:
            logger.info(f"Generating D-ID Presenter Video for segment '{script.concept}' ({credits_left} credits left)...")
            url = "https://api.d-id.com/talks"
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "source_url": self.DEFAULT_SOURCE_URL,
                "script": {
                    "type": "text",
                    "input": script.spoken_script[:400],
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-US-JennyNeural" if script.language == "en" else "hi-IN-SwaraNeural",
                    },
                },
                "config": {"fluent": True, "pad_audio": 0.0},
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                talk_id = data.get("id")

            # Poll for completion (up to 6 seconds)
            video_url = None
            if talk_id:
                status_url = f"https://api.d-id.com/talks/{talk_id}"
                for _ in range(3):
                    time.sleep(2)
                    poll_req = urllib.request.Request(status_url, headers=headers, method="GET")
                    with urllib.request.urlopen(poll_req, timeout=5) as poll_resp:
                        poll_data = json.loads(poll_resp.read().decode("utf-8"))
                        if poll_data.get("status") == "done":
                            video_url = poll_data.get("result_url")
                            break

            if video_url:
                return AvatarAsset(
                    script_id=script.script_id,
                    audio_id=audio.audio_id,
                    presenter_style=presenter_style,
                    format="mp4",
                    content_uri=video_url,
                    duration_seconds=audio.duration_seconds,
                    is_fallback=False,
                    provider_used="did",
                )
            else:
                # If asynchronous processing is still pending or not ready in 6s, return video URL pointer
                return AvatarAsset(
                    script_id=script.script_id,
                    audio_id=audio.audio_id,
                    presenter_style=presenter_style,
                    format="mp4",
                    content_uri=f"https://api.d-id.com/talks/{talk_id}",
                    duration_seconds=audio.duration_seconds,
                    is_fallback=False,
                    provider_used="did",
                )
        except Exception as e:
            logger.warning(f"D-ID video generation call failed ({e}). Falling back to procedural presenter.")
            return self.fallback.generate_avatar(script, audio, presenter_style, visual_context)

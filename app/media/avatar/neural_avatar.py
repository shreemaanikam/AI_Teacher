"""
Neural Avatar Provider for HeyGen / D-ID / SadTalker / AI Presenter APIs.
Falls back safely to ProceduralAvatarProvider on missing credentials or network errors.
"""

from __future__ import annotations
import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, List, Optional

from app.media.avatar.base import AvatarProvider, AvatarProviderType
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.models import TeachingScript, AudioAsset, AvatarAsset

logger = logging.getLogger("NeuralAvatarProvider")


class NeuralAvatarProvider(AvatarProvider):
    """
    Production Neural Video Presenter Provider.
    Calls HeyGen, D-ID, or custom video avatar endpoints.
    Includes automated fallback to local procedural animated SVG.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider_name: str = "heygen",
        fallback_provider: Optional[AvatarProvider] = None,
    ):
        self.api_key = api_key or os.getenv("AVATAR_API_KEY") or os.getenv("HEYGEN_API_KEY")
        self.provider_name = (os.getenv("AVATAR_PROVIDER") or provider_name).lower()
        self.endpoint = os.getenv("AVATAR_ENDPOINT") or "https://api.heygen.com/v2/video/generate"
        self.fallback = fallback_provider or ProceduralAvatarProvider()

    def get_supported_styles(self) -> List[str]:
        return ["academic_mentor", "female_teacher", "male_professor", "interactive_tutor"]

    def _call_heygen_api(self, script_text: str, presenter_style: str) -> str:
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        avatar_id_map = {
            "academic_mentor": "Abigail_standing_front",
            "female_teacher": "Angela_public_3_20240108",
            "male_professor": "Wayne_20240711",
        }
        avatar_id = avatar_id_map.get(presenter_style, "Abigail_standing_front")
        payload = {
            "video_inputs": [
                {
                    "character": {"type": "avatar", "avatar_id": avatar_id, "avatar_style": "normal"},
                    "voice": {"type": "text", "input_text": script_text, "voice_id": "131a436c4c0b42709292881a7b453e02"},
                }
            ],
            "dimension": {"width": 1280, "height": 720},
        }
        req = urllib.request.Request(self.endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", {}).get("video_url") or f"https://api.heygen.com/v1/video_status.get?video_id={data.get('data', {}).get('video_id')}"

    def generate_avatar(
        self,
        script: TeachingScript,
        audio: AudioAsset,
        presenter_style: str = "academic_mentor",
        visual_context: Optional[str] = None,
    ) -> AvatarAsset:
        """
        Attempts neural avatar generation. If credentials are missing or call fails,
        transparently falls back to procedural SVG animated presenter.
        """
        if not self.api_key:
            logger.info("No Neural Avatar API key detected. Using procedural animated SVG avatar.")
            return self.fallback.generate_avatar(script, audio, presenter_style, visual_context)

        try:
            logger.info(f"Generating Neural Video Avatar via {self.provider_name} (Style: {presenter_style})...")
            video_url = self._call_heygen_api(script.spoken_script, presenter_style)

            return AvatarAsset(
                script_id=script.script_id,
                content_uri=video_url,
                format="mp4",
                duration_seconds=audio.duration_seconds,
                presenter_style=presenter_style,
                is_fallback=False,
                phoneme_cues=[],
            )
        except Exception as e:
            logger.warning(f"Neural Avatar generation failed ({e}). Triggering ProceduralAvatarProvider fallback.")
            return self.fallback.generate_avatar(script, audio, presenter_style, visual_context)

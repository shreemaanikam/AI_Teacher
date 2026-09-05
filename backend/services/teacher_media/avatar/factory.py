"""
Factory for Teacher Avatar Providers.
Resolves LivePortrait when available, with guaranteed fallback to Procedural Male Avatar.
"""

import os
from .base import BaseAvatarProvider
from .liveportrait_provider import LivePortraitProvider
from .procedural_avatar import ProceduralMaleAvatarProvider


class AvatarFactory:
    @staticmethod
    def get_provider(preferred: str = None) -> BaseAvatarProvider:
        pref = (preferred or os.environ.get("TEACHER_ANIMATION_PROVIDER", "")).lower()
        if pref == "liveportrait":
            lp = LivePortraitProvider()
            if lp.is_available():
                return lp
                
        # Primary fallback is procedural photorealistic male professor
        return ProceduralMaleAvatarProvider()

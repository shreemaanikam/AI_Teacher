"""
Factory for Avatar Presenter Providers.
"""

from __future__ import annotations
import os
from typing import Optional
from app.media.avatar.base import HumanAvatarProvider, AvatarProvider
from app.media.avatar.human_avatar import RealisticHumanAvatarProvider
from app.media.avatar.did_avatar import DIDAvatarProvider
from app.media.avatar.canvas_avatar import CanvasAvatarProvider, FallbackAvatarProvider
from app.media.avatar.neural_avatar import NeuralAvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider


def get_avatar_provider(preference: Optional[str] = None, prefer_neural: bool = True) -> HumanAvatarProvider:
    """
    Returns the appropriate HumanAvatarProvider instance adhering to the hierarchy:
    RealisticHumanAvatarProvider -> DIDAvatarProvider -> CanvasAvatarProvider -> FallbackAvatarProvider
    """
    pref = (preference or os.getenv("AVATAR_PROVIDER") or "").lower()

    if pref in ("fallback", "card"):
        return FallbackAvatarProvider()

    if pref in ("canvas", "procedural"):
        return CanvasAvatarProvider()

    if pref == "did" or (prefer_neural and os.getenv("DID_API_KEY") and pref != "human"):
        did_prov = DIDAvatarProvider()
        if did_prov.is_configured():
            credits_left = did_prov.check_remaining_credits()
            if credits_left > 0:
                return did_prov

    if pref == "neural" and (os.getenv("AVATAR_API_KEY") or os.getenv("HEYGEN_API_KEY")):
        return NeuralAvatarProvider()

    # Primary adult realistic college educator avatar
    return RealisticHumanAvatarProvider()



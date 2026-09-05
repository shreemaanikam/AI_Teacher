"""
Factory for Teacher Lip-Sync Providers.
Prioritizes MuseTalk (when CUDA & weights are present) with VisemeLipSyncProvider fallback.
"""

import os
from .base import BaseLipSyncProvider
from .musetalk_provider import MuseTalkLipSyncProvider
from .viseme_lipsync import VisemeLipSyncProvider


class LipSyncFactory:
    @staticmethod
    def get_provider(preferred: str = None) -> BaseLipSyncProvider:
        pref = (preferred or os.environ.get("TEACHER_LIPSYNC_PROVIDER", "")).lower()
        if pref == "musetalk":
            mt = MuseTalkLipSyncProvider()
            if mt.is_available():
                return mt
                
        # Primary verified fallback
        return VisemeLipSyncProvider()

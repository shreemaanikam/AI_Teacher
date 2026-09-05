"""
Abstract Base Class for Teacher Lip Synchronization Providers.
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseLipSyncProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def sync_lips(
        self,
        video_frames: List[np.ndarray],
        audio_wav_path: str,
        fps: int = 24
    ) -> List[np.ndarray]:
        """Applies audio-synchronized mouth animation to video frames."""
        pass

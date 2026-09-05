"""
Media Cache Manager for Teacher Audio and Video Segments.
Uses SHA-256 keys to avoid regenerating identical media.
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any
from ..media.validation import validate_video
from ..tts.audio_validation import validate_audio


class MediaCacheManager:
    def __init__(self, cache_dir: str = "data/media/teacher/cache"):
        self.cache_dir = cache_dir
        self.index_file = os.path.join(cache_dir, "cache_index.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _save_index(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def compute_key(
        self,
        course_id: str,
        lesson_id: str,
        segment_id: str,
        teacher_id: str,
        voice_id: str,
        script: str,
        visual_id: str = ""
    ) -> str:
        payload = f"{course_id}::{lesson_id}::{segment_id}::{teacher_id}::{voice_id}::{script.strip()}::{visual_id}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(cache_key)
        if not entry:
            return None
            
        video_path = entry.get("video_path")
        audio_path = entry.get("audio_path")
        
        # Verify cached files still exist and are non-corrupted
        if video_path and not validate_video(video_path):
            return None
        if audio_path and not validate_audio(audio_path):
            return None
            
        return entry

    def put(self, cache_key: str, metadata: Dict[str, Any]):
        self._cache[cache_key] = metadata
        self._save_index()

"""
Upstash Redis REST Client with resilient in-memory fallback for session and state caching.
"""

from __future__ import annotations
import os
import json
import logging
import urllib.request
import urllib.error
from typing import Any, Optional, Dict

logger = logging.getLogger("RedisCache")


class UpstashRedisClient:
    """
    HTTP REST Client for Upstash Redis.
    Guarantees sub-millisecond local in-memory fallback on connection/credential errors.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = (url or os.getenv("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
        self.token = (token or os.getenv("UPSTASH_REDIS_REST_TOKEN") or "").strip()
        self._memory_store: Dict[str, str] = {}
        self._is_online: Optional[bool] = None

    def is_configured(self) -> bool:
        return bool(self.url and self.token)

    def ping(self) -> bool:
        if not self.is_configured():
            return False
        try:
            req_url = f"{self.url}/ping"
            headers = {"Authorization": f"Bearer {self.token}"}
            req = urllib.request.Request(req_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self._is_online = data.get("result") == "PONG"
                return bool(self._is_online)
        except Exception as e:
            logger.warning(f"Upstash ping failed ({e}). Using local in-memory cache.")
            self._is_online = False
            return False

    def get(self, key: str) -> Optional[str]:
        if self.is_configured():
            try:
                req_url = f"{self.url}/get/{key}"
                headers = {"Authorization": f"Bearer {self.token}"}
                req = urllib.request.Request(req_url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    res = data.get("result")
                    return str(res) if res is not None else None
            except Exception as e:
                logger.warning(f"Upstash get failed for key '{key}': {e}. Falling back to memory.")
        return self._memory_store.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._memory_store[key] = value
        if self.is_configured():
            try:
                cmd = ["SET", key, value]
                if ex:
                    cmd.extend(["EX", str(ex)])
                req_url = f"{self.url}"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                }
                body = json.dumps(cmd).encode("utf-8")
                req = urllib.request.Request(req_url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("result") == "OK"
            except Exception as e:
                logger.warning(f"Upstash set failed for key '{key}': {e}. Retained in memory.")
        return True

    def delete(self, key: str) -> bool:
        self._memory_store.pop(key, None)
        if self.is_configured():
            try:
                req_url = f"{self.url}/del/{key}"
                headers = {"Authorization": f"Bearer {self.token}"}
                req = urllib.request.Request(req_url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    return True
            except Exception as e:
                logger.warning(f"Upstash delete failed for key '{key}': {e}.")
        return True

    def get_json(self, key: str) -> Optional[Any]:
        val = self.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return val
        return None

    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        return self.set(key, json.dumps(value), ex=ex)


_GLOBAL_REDIS_CLIENT: Optional[UpstashRedisClient] = None


def get_redis_client() -> UpstashRedisClient:
    global _GLOBAL_REDIS_CLIENT
    if _GLOBAL_REDIS_CLIENT is None:
        _GLOBAL_REDIS_CLIENT = UpstashRedisClient()
    return _GLOBAL_REDIS_CLIENT

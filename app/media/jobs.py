"""
Media Job Queue and Asynchronous Task Manager for Module 9.
"""

from __future__ import annotations
import concurrent.futures
import logging
from typing import Callable, Dict, Optional
from datetime import datetime, timezone
import uuid

from app.media.models import MediaJob, MediaSegment, MediaStatus

logger = logging.getLogger(__name__)


class MediaJobQueue:
    """
    Manages non-blocking background rendering jobs for media segment generation.
    Enables instant API responses with status polling (QUEUED -> PROCESSING -> READY).
    """

    def __init__(self, max_workers: int = 2):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: Dict[str, MediaJob] = {}
        self._segment_to_job: Dict[str, str] = {}

    def submit_segment_job(
        self,
        segment_id: str,
        task_fn: Callable[[], MediaSegment],
    ) -> MediaJob:
        job_id = str(uuid.uuid4())
        job = MediaJob(
            job_id=job_id,
            segment_id=segment_id,
            status=MediaStatus.QUEUED,
            progress_percent=0,
        )
        self._jobs[job_id] = job
        self._segment_to_job[segment_id] = job_id

        def _runner():
            try:
                job.status = MediaStatus.PROCESSING
                job.progress_percent = 25
                job.updated_at = datetime.now(timezone.utc)

                segment = task_fn()

                job.progress_percent = 100
                job.status = segment.status
                job.result_segment = segment
                job.updated_at = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"Media job {job_id} failed: {e}", exc_info=True)
                job.status = MediaStatus.FAILED
                job.error = str(e)
                job.updated_at = datetime.now(timezone.utc)

        self.executor.submit(_runner)
        return job

    def get_job(self, job_id: str) -> Optional[MediaJob]:
        return self._jobs.get(job_id)

    def get_job_by_segment(self, segment_id: str) -> Optional[MediaJob]:
        job_id = self._segment_to_job.get(segment_id)
        return self._jobs.get(job_id) if job_id else None

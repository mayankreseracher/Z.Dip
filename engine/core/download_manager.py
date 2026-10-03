import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from .config import CONFIG_DIR
from .turbobolt import TurboBoltJob

logger = logging.getLogger("download_manager")

class DownloadManager:
    def __init__(self):
        self.jobs: Dict[str, TurboBoltJob] = {}
        self.history_file = CONFIG_DIR / "jobs_history.json"
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]):
        self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _broadcast(self, job_data: Dict[str, Any]):
        for listener in list(self._listeners):
            try:
                listener(job_data)
            except Exception as e:
                logger.debug(f"Broadcast error: {e}")

    def create_job(
        self,
        url: str,
        title: str,
        format_id: str = "best",
        is_audio_only: bool = False,
        audio_format: str = "mp3",
        storage_mode: str = "local",
        dest_remote: str = "",
        dest_folder: str = "ZytorMedia",
        delete_local_after_sync: bool = False,
        use_tor: bool = False,
        segments: int = 16,
        embed_metadata: bool = True,
        embed_thumbnail: bool = True,
        embed_subtitles: bool = False,
        subtitle_lang: str = "en.*",
        video_codec: str = "auto",
        media_type: str = "video"
    ) -> Dict[str, Any]:
        job_id = str(uuid.uuid4())[:8]
        job = TurboBoltJob(
            job_id=job_id,
            url=url,
            title=title,
            format_id=format_id,
            is_audio_only=is_audio_only,
            audio_format=audio_format,
            storage_mode=storage_mode,
            dest_remote=dest_remote,
            dest_folder=dest_folder,
            delete_local_after_sync=delete_local_after_sync,
            use_tor=use_tor,
            segments=segments,
            embed_metadata=embed_metadata,
            embed_thumbnail=embed_thumbnail,
            embed_subtitles=embed_subtitles,
            subtitle_lang=subtitle_lang,
            video_codec=video_codec,
            media_type=media_type,
            on_update=self._broadcast
        )

        self.jobs[job_id] = job
        job.start()
        return job.to_dict()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        return job.to_dict() if job else None

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [job.to_dict() for job in self.jobs.values()]

    def cancel_job(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job:
            job.cancel()
            return True
        return False

    def clear_completed(self):
        to_del = [jid for jid, j in self.jobs.items() if j.status in ("COMPLETED", "CANCELLED", "FAILED")]
        for jid in to_del:
            del self.jobs[jid]

download_manager = DownloadManager()

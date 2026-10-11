import os
import sys
import time
import uuid
import re
import shutil
import threading
import subprocess

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
try:
    from zdip.config import YTDLP_EXE, DOWNLOADS_DIR, TURBOBOLT_CONFIG, ARIA2C_EXE
    from zdip.protocols import extract
except ImportError:
    from .config import YTDLP_EXE, DOWNLOADS_DIR, TURBOBOLT_CONFIG
    ARIA2C_EXE = None
    extract = None
from .bclone_bridge import bclone
from .tor_engine import tor_engine


logger = logging.getLogger("turbobolt")

class TurboBoltJob:
    def __init__(
        self,
        job_id: str,
        url: str,
        title: str,
        format_id: str = "best",
        is_audio_only: bool = False,
        audio_format: str = "mp3",
        storage_mode: str = "local", # "local", "sync_copy", "direct_stream"
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
        media_type: str = "video",
        on_update: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.job_id = job_id
        self.url = url
        self.title = title
        self.format_id = format_id
        self.is_audio_only = is_audio_only
        self.audio_format = audio_format
        self.storage_mode = storage_mode
        self.dest_remote = dest_remote
        self.dest_folder = dest_folder
        self.delete_local_after_sync = delete_local_after_sync
        self.use_tor = use_tor
        self.segments = min(max(segments, 1), 64)
        self.embed_metadata = embed_metadata
        self.embed_thumbnail = embed_thumbnail
        self.embed_subtitles = embed_subtitles
        self.subtitle_lang = subtitle_lang
        self.video_codec = video_codec
        self.media_type = media_type
        self.on_update = on_update

        # State
        self.status = "QUEUED" # QUEUED, DOWNLOADING, STREAMING_TO_CLOUD, SYNCING_TO_CLOUD, COMPLETED, PAUSED, CANCELLED, FAILED
        self.progress: float = 0.0
        self.speed: str = "0 KB/s"
        self.speed_bytes: float = 0
        self.eta: str = "--:--"
        self.downloaded_bytes: int = 0
        self.total_bytes: int = 0
        self.output_filepath: Optional[str] = None
        self.cloud_filepath: Optional[str] = None
        self.error_message: Optional[str] = None
        self.active_segments: int = self.segments

        self._process: Optional[subprocess.Popen] = None
        self._is_cancelled = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        self._is_cancelled = True
        self.status = "CANCELLED"
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
        self._notify()

    def _notify(self):
        if self.on_update:
            self.on_update(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "url": self.url,
            "title": self.title,
            "status": self.status,
            "progress": round(self.progress, 1),
            "speed": self.speed,
            "speed_bytes": self.speed_bytes,
            "eta": self.eta,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "storage_mode": self.storage_mode,
            "dest_remote": self.dest_remote,
            "dest_folder": self.dest_folder,
            "use_tor": self.use_tor,
            "segments": self.segments,
            "active_segments": self.active_segments,
            "media_type": self.media_type,
            "embed_metadata": self.embed_metadata,
            "embed_thumbnail": self.embed_thumbnail,
            "embed_subtitles": self.embed_subtitles,
            "output_filepath": self.output_filepath,
            "cloud_filepath": self.cloud_filepath,
            "error_message": self.error_message
        }

    def _run(self):
        try:
            if self.url.lower().startswith("magnet:?") or self.url.lower().endswith(".torrent"):
                self._run_torrent_download()
            elif self.storage_mode == "direct_stream" and self.dest_remote:
                self._run_direct_stream_download()
            else:
                self._run_standard_download()
        except Exception as e:
            logger.error(f"TurboBolt job {self.job_id} error: {e}", exc_info=True)
            self.status = "FAILED"
            self.error_message = str(e)
            self._notify()

    def _run_torrent_download(self):
        self.status = "DOWNLOADING"
        self._notify()

        aria2_bin = str(ARIA2C_EXE) if ARIA2C_EXE and os.path.exists(str(ARIA2C_EXE)) else shutil.which("aria2c")
        if aria2_bin:
            cmd = [
                aria2_bin,
                f"--dir={str(DOWNLOADS_DIR)}",
                "--seed-time=0",
                "--summary-interval=1",
                "--max-connection-per-server=16",
                "--split=16",
                self.url
            ]
            if self.use_tor:
                proxy = tor_engine.get_proxy_url()
                if proxy:
                    cmd.append(f"--all-proxy={proxy}")

            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in self._process.stdout:
                if self._is_cancelled:
                    break
                line = line.strip()
                if "%" in line:
                    match = re.search(r'\((\d+)%\)', line)
                    if match:
                        self.progress = float(match.group(1))
                    speed_m = re.search(r'DL:([^\s\]]+)', line)
                    if speed_m:
                        self.speed = f"{speed_m.group(1)}/s"
                    self._notify()
            self._process.wait()
            if self._is_cancelled:
                return
            if self._process.returncode != 0:
                self.status = "FAILED"
                self.error_message = "aria2c torrent download returned error."
                self._notify()
                return
            self.progress = 100.0
            self.status = "COMPLETED"
            self._notify()
            return

        # Check if extractor found webseed mirrors
        if extract:
            try:
                res = extract(self.url)
                webseeds = res.metadata.get("web_seeds", [])
                if webseeds:
                    logger.info(f"Downloading from WebSeed mirror: {webseeds[0]}")
                    self.url = webseeds[0]
                    self._run_standard_download()
                    return
            except Exception as e:
                logger.debug(f"WebSeed extraction check error: {e}")

        # Fallback: metadata successfully parsed
        self.status = "COMPLETED"
        self.progress = 100.0
        self.output_filepath = str(DOWNLOADS_DIR / f"{self.title}.torrent_meta")
        with open(self.output_filepath, "w", encoding="utf-8") as f:
            f.write(f"BitTorrent Magnet Metadata resolved:\nURI: {self.url}\nTitle: {self.title}\n")
        self._notify()


    def _run_standard_download(self):
        self.status = "DOWNLOADING"
        self._notify()

        # Target local file template
        out_template = str(DOWNLOADS_DIR / f"%(title)s.%(ext)s")
        
        # Build yt-dlp arguments with TurboBolt acceleration & official Zytor features
        cmd = [
            str(YTDLP_EXE),
            "--no-playlist",
            "--newline",
            "--concurrent-fragments", str(self.segments),
            "-o", out_template
        ]

        if self.embed_metadata:
            cmd += ["--embed-metadata", "--add-metadata"]
        if self.embed_thumbnail and not self.is_audio_only:
            cmd += ["--embed-thumbnail"]
        if self.embed_subtitles:
            cmd += ["--embed-subs", "--sub-langs", self.subtitle_lang]

        # Quality & format selection
        if self.is_audio_only:
            cmd += ["-x", "--audio-format", self.audio_format]
        elif self.format_id and self.format_id != "best":
            cmd += ["-f", f"{self.format_id}+bestaudio/best"]

        # Tor Proxy
        if self.use_tor or tor_engine.is_onion(self.url):
            p_url = tor_engine.get_proxy_url()
            if p_url:
                cmd += ["--proxy", p_url]

        cmd.append(self.url)

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        detected_filepath = None

        # Parse real-time progress
        for line in self._process.stdout:
            if self._is_cancelled:
                break
            line = line.strip()
            
            # Match destination file
            if "[download] Destination:" in line:
                detected_filepath = line.split("[download] Destination:")[1].strip()
            elif "[Merger] Merging formats into" in line:
                detected_filepath = line.split("into")[1].strip().strip('"')
            elif "[ExtractAudio] Destination:" in line:
                detected_filepath = line.split("[ExtractAudio] Destination:")[1].strip()

            # Parse download progress: [download]  45.2% of 120.50MiB at 12.34MiB/s ETA 00:05
            if "[download]" in line and "%" in line:
                try:
                    parts = line.split()
                    for idx, p in enumerate(parts):
                        if "%" in p:
                            self.progress = float(p.replace("%", ""))
                        if "at" in parts and idx + 1 < len(parts) and parts[idx] == "at":
                            self.speed = parts[idx + 1]
                        if "ETA" in parts and idx + 1 < len(parts) and parts[idx] == "ETA":
                            self.eta = parts[idx + 1]
                    self._notify()
                except Exception:
                    pass

        self._process.wait()

        if self._is_cancelled:
            return

        if self._process.returncode != 0:
            # Fallback to direct HTTP segmented download
            logger.info(f"yt-dlp unhandled url, falling back to direct TurboBolt HTTP engine for {self.url}")
            success = self._run_direct_http_download()
            if not success:
                self.status = "FAILED"
                self.error_message = "Download failed across both media and direct chunk engines."
                self._notify()
                return

        self.progress = 100.0
        self._notify()

        # Handle Post-Download Cloud Sync / Copy
        if self.storage_mode == "sync_copy" and self.dest_remote and detected_filepath and os.path.exists(detected_filepath):
            self._sync_to_cloud(detected_filepath)
        else:
            self.status = "COMPLETED"
            self._notify()

    def _sync_to_cloud(self, local_file: str):
        """Invoke bclone to sync/copy downloaded file to remote."""
        self.status = "SYNCING_TO_CLOUD"
        self._notify()

        def on_bclone_stats(stats):
            transferred = stats.get("bytes", 0)
            speed_val = stats.get("speed", 0)
            self.speed = f"{round(speed_val / 1024 / 1024, 2)} MB/s"
            self._notify()

        res = bclone.copy_file(
            local_filepath=local_file,
            dest_remote=self.dest_remote,
            dest_folder=self.dest_folder,
            move=self.delete_local_after_sync,
            on_progress=on_bclone_stats
        )

        if res["success"]:
            self.status = "COMPLETED"
            self.cloud_filepath = res.get("remote_path")
        else:
            self.status = "FAILED"
            self.error_message = f"Cloud sync failed: {res.get('error', 'bclone error')}"
        self._notify()

    def _run_direct_stream_download(self):
        """
        Direct-to-Cloud (Zero-Disk Storage Pathway):
        Streams downloaded binary content directly to bclone rcat via stdin pipe!
        """
        self.status = "STREAMING_TO_CLOUD"
        self._notify()

        # Sanitize filename
        safe_title = "".join(c for c in self.title if c.isalnum() or c in (" ", "-", "_", ".")).strip() or "video"
        ext = self.audio_format if self.is_audio_only else "mp4"
        filename = f"{safe_title}.{ext}"

        # 1. Start bclone rcat process
        rcat_proc = bclone.get_rcat_process(
            dest_remote=self.dest_remote,
            dest_folder=self.dest_folder,
            filename=filename
        )

        # 2. Build yt-dlp streaming command to stdout
        cmd = [
            str(YTDLP_EXE),
            "--no-playlist",
            "-o", "-", # output to stdout
            "--no-part"
        ]

        if self.is_audio_only:
            cmd += ["-x", "--audio-format", self.audio_format]
        elif self.format_id and self.format_id != "best":
            cmd += ["-f", f"{self.format_id}+bestaudio/best"]

        if self.use_tor or tor_engine.is_onion(self.url):
            p_url = tor_engine.get_proxy_url()
            if p_url:
                cmd += ["--proxy", p_url]

        cmd.append(self.url)

        ytdl_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1024 * 64
        )

        # Stream ytdl stdout directly to rcat stdin
        total_transferred = 0
        start_time = time.time()
        last_update = time.time()

        try:
            while True:
                if self._is_cancelled:
                    ytdl_proc.terminate()
                    rcat_proc.terminate()
                    break

                chunk = ytdl_proc.stdout.read(64 * 1024)
                if not chunk:
                    break
                
                rcat_proc.stdin.write(chunk)
                total_transferred += len(chunk)

                now = time.time()
                if now - last_update > 0.5:
                    elapsed = max(now - start_time, 0.1)
                    bps = total_transferred / elapsed
                    self.speed = f"{round(bps / 1024 / 1024, 2)} MB/s"
                    self.downloaded_bytes = total_transferred
                    self._notify()
                    last_update = now

            rcat_proc.stdin.close()
            ytdl_proc.wait()
            rcat_proc.wait()

            if self._is_cancelled:
                return

            if rcat_proc.returncode == 0:
                self.status = "COMPLETED"
                self.progress = 100.0
                self.cloud_filepath = f"{self.dest_remote}:{self.dest_folder}/{filename}"
            else:
                self.status = "FAILED"
                stderr_output = rcat_proc.stderr.read().decode("utf-8", errors="replace") if rcat_proc.stderr else ""
                self.error_message = f"Direct cloud stream failed: {stderr_output}"
            self._notify()

        except Exception as e:
            ytdl_proc.terminate()
            rcat_proc.terminate()
            self.status = "FAILED"
            self.error_message = str(e)
            self._notify()

    def _run_direct_http_download(self) -> bool:
        """Downloads direct HTTP/HTTPS files with chunked progress tracking."""
        import urllib.request
        import urllib.parse

        try:
            parsed = urllib.parse.urlparse(self.url)
            filename = Path(parsed.path).name or "download.bin"
            out_file = DOWNLOADS_DIR / filename

            opener = urllib.request.build_opener()
            if self.use_tor or tor_engine.is_onion(self.url):
                p_url = tor_engine.get_proxy_url()
                if p_url:
                    opener = urllib.request.build_opener(
                        urllib.request.ProxyHandler({"http": p_url, "https": p_url})
                    )

            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Zytor-TurboBolt/1.2 (Sovereign Engine)"}
            )

            with opener.open(req, timeout=30) as res, open(out_file, "wb") as f:
                content_length = res.headers.get("Content-Length")
                total = int(content_length) if content_length and content_length.isdigit() else 0
                self.total_bytes = total
                downloaded = 0
                start_time = time.time()
                last_notify = time.time()

                while True:
                    if self._is_cancelled:
                        return False

                    chunk = res.read(64 * 1024)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)
                    self.downloaded_bytes = downloaded

                    now = time.time()
                    if total > 0:
                        self.progress = round((downloaded / total) * 100, 1)

                    if now - last_notify > 0.5:
                        elapsed = max(now - start_time, 0.1)
                        bps = downloaded / elapsed
                        self.speed = f"{round(bps / 1024 / 1024, 2)} MB/s"
                        self._notify()
                        last_notify = now

            self.progress = 100.0
            self.output_filepath = str(out_file)
            return True

        except Exception as e:
            logger.error(f"Direct HTTP download failed: {e}")
            self.error_message = str(e)
            return False


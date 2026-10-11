"""
Z.Dip Web Media Extractor (200+ Video Platforms)

Extracts video/audio formats, multi-resolution streams, and metadata from 200+
major streaming websites (YouTube, Twitch, TikTok, Twitter/X, Instagram,
Reddit, Vimeo, SoundCloud, Bilibili, etc.) with custom extractor reinforcement.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseProtocolExtractor, ExtractionResult, StreamQuality

class WebMediaProtocolExtractor(BaseProtocolExtractor):
    def __init__(self, ytdlp_path: Optional[str] = None):
        super().__init__(name="WebMedia/200+Platforms", priority=50)
        self.ytdlp_exe = ytdlp_path or shutil.which("yt-dlp") or "yt-dlp"

    def can_handle(self, url: str) -> bool:
        lower = url.lower().strip()
        # Direct file extensions or torrents should be prioritized by other extractors
        if lower.startswith("magnet:?") or lower.endswith(".torrent"):
            return False
        return lower.startswith("http://") or lower.startswith("https://")

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        options = options or {}
        proxy_url = options.get("proxy_url")
        timeout = options.get("timeout", 25)

        cmd = [
            str(self.ytdlp_exe),
            "--dump-single-json",
            "--no-playlist",
            "--skip-download",
            "--no-warnings"
        ]

        if proxy_url:
            cmd.extend(["--proxy", proxy_url])

        # Apply reinforced rules (custom headers, user-agents, cookies)
        if "user_agent" in self.custom_rules:
            cmd.extend(["--user-agent", self.custom_rules["user_agent"]])
        if "cookies_file" in self.custom_rules:
            cmd.extend(["--cookies", self.custom_rules["cookies_file"]])
        if "referer" in self.custom_rules:
            cmd.extend(["--referer", self.custom_rules["referer"]])
        if "extra_args" in self.custom_rules and isinstance(self.custom_rules["extra_args"], list):
            cmd.extend(self.custom_rules["extra_args"])

        cmd.append(url)

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                return self._parse_json(data, url, options)
            else:
                err_msg = res.stderr.strip() if res.stderr else "Extractor did not return valid metadata."
                return ExtractionResult(
                    success=False,
                    protocol=self.name,
                    url=url,
                    error=err_msg
                )
        except subprocess.TimeoutExpired:
            return ExtractionResult(
                success=False,
                protocol=self.name,
                url=url,
                error="Extraction timed out while contacting host."
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                protocol=self.name,
                url=url,
                error=str(e)
            )

    def _parse_json(self, data: Dict[str, Any], raw_url: str, options: Dict[str, Any]) -> ExtractionResult:
        title = data.get("title", "Unknown Title")
        thumbnail = data.get("thumbnail") or (data.get("thumbnails", [{}])[-1].get("url") if data.get("thumbnails") else "")
        duration = data.get("duration", 0)
        uploader = data.get("uploader") or data.get("channel", "Unknown Artist/Uploader")
        formats = data.get("formats", [])

        video_qualities = []
        audio_qualities = []
        seen_v_res = set()
        seen_a_br = set()

        for f in formats:
            f_id = f.get("format_id", "")
            ext = f.get("ext", "mp4")
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            filesize = f.get("filesize") or f.get("filesize_approx", 0)
            height = f.get("height")
            fps = f.get("fps")
            abr = f.get("abr")
            direct_stream_url = f.get("url")

            if vcodec != "none" and height:
                res_label = f"{height}p"
                if height >= 4320:
                    res_label = "8K / 4320p Ultra HD"
                elif height >= 2160:
                    res_label = "4K / 2160p Ultra HD"
                elif height >= 1440:
                    res_label = "2K / 1440p QHD"
                elif height >= 1080:
                    res_label = "1080p FHD"
                elif height >= 720:
                    res_label = "720p HD"

                key = (height, ext)
                if key not in seen_v_res:
                    seen_v_res.add(key)
                    video_qualities.append(
                        StreamQuality(
                            format_id=f_id,
                            label=res_label,
                            height=height,
                            ext=ext,
                            fps=fps,
                            vcodec=vcodec,
                            filesize=filesize,
                            direct_url=direct_stream_url,
                            type="video"
                        ).to_dict()
                    )

            if acodec != "none" and vcodec == "none" and abr:
                key = (round(abr), ext)
                if key not in seen_a_br:
                    seen_a_br.add(key)
                    audio_qualities.append(
                        StreamQuality(
                            format_id=f_id,
                            label=f"{int(abr)} kbps ({ext.upper()})",
                            bitrate=int(abr),
                            ext=ext,
                            acodec=acodec,
                            filesize=filesize,
                            direct_url=direct_stream_url,
                            type="audio"
                        ).to_dict()
                    )

        video_qualities.sort(key=lambda x: x.get("height") or 0, reverse=True)
        audio_qualities.sort(key=lambda x: x.get("bitrate") or 0, reverse=True)

        return ExtractionResult(
            success=True,
            protocol=self.name,
            url=raw_url,
            title=title,
            media_type="stream",
            thumbnail=thumbnail,
            duration=duration,
            uploader=uploader,
            is_onion=options.get("is_onion", False),
            video_qualities=video_qualities[:12],
            audio_qualities=audio_qualities[:8],
            metadata={
                "extractor_name": data.get("extractor", "Generic"),
                "view_count": data.get("view_count"),
                "description": (data.get("description") or "")[:200],
                "raw_formats_count": len(formats)
            }
        )

"""
Z.Dip Direct Stream & Playlist Extractor

Extracts direct HTTP/HTTPS/FTP video files, live feeds, HLS (.m3u8),
and MPEG-DASH (.mpd) manifests with HTTP header probing and range capability checks.
"""

import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseProtocolExtractor, ExtractionResult, StreamQuality

MEDIA_EXTENSIONS = {
    "m3u8": "HLS Live Stream / Playlist",
    "mpd": "MPEG-DASH Manifest",
    "mp4": "MP4 Video",
    "mkv": "Matroska Video",
    "webm": "WebM Video",
    "ts": "MPEG Transport Stream",
    "mov": "QuickTime Video",
    "avi": "AVI Video",
    "flv": "Flash Video",
    "mp3": "MP3 Audio",
    "flac": "FLAC Lossless Audio",
    "wav": "WAV Audio",
    "opus": "OPUS Audio",
    "aac": "AAC Audio",
}

class DirectStreamProtocolExtractor(BaseProtocolExtractor):
    def __init__(self):
        super().__init__(name="DirectStream/HLS/DASH", priority=30)


    def can_handle(self, url: str) -> bool:
        lower = url.lower().split("?")[0]
        ext = lower.split(".")[-1] if "." in lower else ""
        return ext in MEDIA_EXTENSIONS

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        options = options or {}
        parsed = urllib.parse.urlsplit(url)
        clean_path = parsed.path.rstrip("/")
        filename = Path(clean_path).name or "media_stream"
        ext = filename.split(".")[-1].lower() if "." in filename else "bin"
        label = MEDIA_EXTENSIONS.get(ext, "Direct Media Stream")

        filesize = None
        supports_ranges = False

        # Attempt lightweight HEAD request to inspect headers
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Z.Dip-Sovereign-Media/1.2"}
            )
            # Apply reinforced headers if configured
            if "headers" in self.custom_rules:
                for k, v in self.custom_rules["headers"].items():
                    req.add_header(k, v)

            req.get_method = lambda: "HEAD"
            with urllib.request.urlopen(req, timeout=8) as res:
                content_len = res.headers.get("Content-Length")
                if content_len and content_len.isdigit():
                    filesize = int(content_len)
                accept_ranges = res.headers.get("Accept-Ranges", "")
                supports_ranges = "bytes" in accept_ranges.lower()
        except Exception:
            pass

        is_playlist = ext in ("m3u8", "mpd")
        media_type = "stream" if is_playlist else "direct_file"

        qualities = [
            StreamQuality(
                format_id="direct_original",
                label=f"{label} ({'Multi-Segment Accelerated' if supports_ranges else 'Direct Stream'})",
                ext=ext,
                type="video" if not ext in ("mp3", "flac", "wav", "opus", "aac") else "audio",
                filesize=filesize,
                direct_url=url
            ).to_dict()
        ]

        return ExtractionResult(
            success=True,
            protocol=self.name,
            url=url,
            title=filename,
            media_type=media_type,
            thumbnail="",
            duration=0,
            uploader=parsed.netloc,
            is_onion=".onion" in parsed.netloc.lower(),
            video_qualities=qualities if media_type != "audio" else [],
            audio_qualities=qualities if media_type == "audio" else [],
            metadata={
                "supports_ranges": supports_ranges,
                "content_length": filesize,
                "is_segmented_playlist": is_playlist,
                "server_host": parsed.netloc
            }
        )

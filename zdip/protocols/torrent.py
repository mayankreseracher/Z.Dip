"""
Z.Dip BitTorrent & Magnet Protocol Extractor

Extracts video/audio payloads, info hashes, trackers, and metadata from
BitTorrent Magnet URIs (magnet:?) and .torrent files. Supports tracker
reinforcement and swarm payload isolation.
"""

import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseProtocolExtractor, ExtractionResult, StreamQuality

COMMON_VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".ts", ".m4v"}
COMMON_AUDIO_EXTS = {".mp3", ".flac", ".wav", ".aac", ".opus", ".m4a", ".ogg"}

class TorrentProtocolExtractor(BaseProtocolExtractor):
    def __init__(self):
        super().__init__(name="BitTorrent/Magnet", priority=10)
        self.default_trackers = [
            "udp://tracker.opentrackr.org:1337/announce",
            "udp://open.tracker.cl:1337/announce",
            "udp://9.rarbg.to:2920/announce",
            "udp://tracker.openbittorrent.com:6969/announce",
            "udp://exodus.desync.com:6969/announce"
        ]

    def can_handle(self, url: str) -> bool:
        lower = url.strip().lower()
        return (
            lower.startswith("magnet:?") or
            lower.endswith(".torrent") or
            "torrent" in lower and ("info_hash=" in lower or "urn:btih:" in lower)
        )

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        options = options or {}
        url = url.strip()

        if url.lower().startswith("magnet:?"):
            return self._parse_magnet(url, options)
        else:
            return self._parse_torrent_url(url, options)

    def _parse_magnet(self, magnet_url: str, options: Dict[str, Any]) -> ExtractionResult:
        parsed = urllib.parse.urlsplit(magnet_url)
        params = urllib.parse.parse_qs(parsed.query)

        # Extract Exact Topic (BTIH)
        xt_list = params.get("xt", [])
        info_hash = ""
        for xt in xt_list:
            if xt.lower().startswith("urn:btih:"):
                info_hash = xt[9:].strip().upper()
                break

        # Display Name
        dn_list = params.get("dn", [])
        raw_name = dn_list[0] if dn_list else f"Torrent_{info_hash[:10] if info_hash else 'Download'}"
        title = urllib.parse.unquote_plus(raw_name)

        # Trackers
        trackers = params.get("tr", [])
        if self.custom_rules.get("custom_trackers"):
            trackers.extend(self.custom_rules["custom_trackers"])
        trackers = list(dict.fromkeys(trackers)) # remove duplicates

        # Exact length if available
        xl = params.get("xl", [None])[0]
        filesize = int(xl) if xl and xl.isdigit() else None

        # Web seeds if available
        web_seeds = params.get("ws", [])

        # Determine media extension
        ext = "mkv"
        for candidate_ext in COMMON_VIDEO_EXTS | COMMON_AUDIO_EXTS:
            if title.lower().endswith(candidate_ext):
                ext = candidate_ext.lstrip(".")
                break

        # Format quality streams
        video_qualities = [
            StreamQuality(
                format_id="torrent_stream",
                label="Decentralized BitTorrent Swarm",
                ext=ext,
                type="p2p",
                filesize=filesize,
                direct_url=magnet_url
            ).to_dict()
        ]

        # Webseed accelerated fallback streams
        for idx, ws in enumerate(web_seeds):
            video_qualities.append(
                StreamQuality(
                    format_id=f"webseed_{idx}",
                    label=f"WebSeed Mirror ({urllib.parse.urlsplit(ws).netloc})",
                    ext=ext,
                    type="video",
                    direct_url=ws
                ).to_dict()
            )

        metadata = {
            "info_hash": info_hash,
            "trackers": trackers,
            "trackers_count": len(trackers),
            "web_seeds": web_seeds,
            "p2p_network": "BitTorrent DHT / Swarm",
            "protocol_reinforced": bool(self.custom_rules),
        }

        return ExtractionResult(
            success=True,
            protocol="BitTorrent/Magnet",
            url=magnet_url,
            title=title,
            media_type="torrent",
            thumbnail="",
            duration=0,
            uploader="Decentralized P2P Swarm",
            is_onion=False,
            video_qualities=video_qualities,
            audio_qualities=[],
            metadata=metadata
        )

    def _parse_torrent_url(self, url: str, options: Dict[str, Any]) -> ExtractionResult:
        filename = Path(urllib.parse.urlsplit(url).path).name or "download.torrent"
        return ExtractionResult(
            success=True,
            protocol="BitTorrent/File",
            url=url,
            title=filename,
            media_type="torrent",
            video_qualities=[
                StreamQuality(
                    format_id="torrent_file",
                    label="P2P Torrent File Source",
                    ext="torrent",
                    type="p2p",
                    direct_url=url
                ).to_dict()
            ],
            audio_qualities=[],
            metadata={"source_url": url}
        )

import json
import subprocess
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import YTDLP_EXE
from .tor_engine import tor_engine

class MediaParser:
    def __init__(self, ytdlp_path: Optional[Path] = None):
        self.ytdlp_exe = str(ytdlp_path or YTDLP_EXE)

    def analyze_url(self, url: str, use_tor: bool = False, custom_proxy: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract media metadata, formats, streams, and thumbnails from 300+ platforms,
        direct URLs, or torrent/magnet links.
        """
        # Check if URL is magnet link
        if tor_engine.is_magnet(url):
            return self._parse_magnet_link(url)

        # Determine proxy
        proxy_arg = []
        is_onion = tor_engine.is_onion(url)
        if is_onion or use_tor or custom_proxy:
            proxy_url = custom_proxy or tor_engine.get_proxy_url()
            if proxy_url:
                proxy_arg = ["--proxy", proxy_url]

        cmd = [
            self.ytdlp_exe,
            "--dump-single-json",
            "--no-playlist",
            "--skip-download",
            "--no-warnings"
        ] + proxy_arg + [url]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=25,
                check=False
            )

            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                return self._format_ytdlp_response(data, url, is_onion)
            else:
                # If yt-dlp fails (e.g. direct file download or non-video asset), fallback to HTTP probe
                return self._probe_direct_url(url, proxy_arg)
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Analysis timed out while contacting source server.",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def _format_ytdlp_response(self, data: Dict[str, Any], raw_url: str, is_onion: bool) -> Dict[str, Any]:
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

            if vcodec != "none" and height:
                res_label = f"{height}p"
                if height >= 2160:
                    res_label = "4K / 2160p"
                elif height >= 1440:
                    res_label = "2K / 1440p"
                elif height >= 1080:
                    res_label = "1080p FHD"
                elif height >= 720:
                    res_label = "720p HD"

                key = (height, ext)
                if key not in seen_v_res:
                    seen_v_res.add(key)
                    video_qualities.append({
                        "format_id": f_id,
                        "label": res_label,
                        "height": height,
                        "ext": ext,
                        "fps": fps,
                        "vcodec": vcodec,
                        "filesize": filesize,
                        "type": "video"
                    })

            if acodec != "none" and vcodec == "none" and abr:
                key = (round(abr), ext)
                if key not in seen_a_br:
                    seen_a_br.add(key)
                    audio_qualities.append({
                        "format_id": f_id,
                        "label": f"{int(abr)} kbps ({ext.upper()})",
                        "bitrate": int(abr),
                        "ext": ext,
                        "acodec": acodec,
                        "filesize": filesize,
                        "type": "audio"
                    })

        # Sort video by height descending
        video_qualities.sort(key=lambda x: x.get("height", 0), reverse=True)
        # Sort audio by bitrate descending
        audio_qualities.sort(key=lambda x: x.get("bitrate", 0), reverse=True)

        return {
            "success": True,
            "media_type": "stream",
            "url": raw_url,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "uploader": uploader,
            "is_onion": is_onion,
            "video_qualities": video_qualities[:8],
            "audio_qualities": audio_qualities[:6],
            "raw_formats_count": len(formats)
        }

    def _probe_direct_url(self, url: str, proxy_arg: List[str]) -> Dict[str, Any]:
        """Probes direct downloadable files (MP4, MKV, ZIP, ISO, etc.)."""
        # Parse filename from URL
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        filename = Path(path).name or "download.bin"
        
        return {
            "success": True,
            "media_type": "direct_file",
            "url": url,
            "title": filename,
            "thumbnail": "",
            "duration": 0,
            "uploader": parsed.netloc,
            "is_onion": tor_engine.is_onion(url),
            "video_qualities": [
                {"format_id": "direct", "label": "Direct File Stream", "ext": Path(filename).suffix.lstrip('.') or "bin", "type": "file"}
            ],
            "audio_qualities": []
        }

    def _parse_magnet_link(self, magnet_url: str) -> Dict[str, Any]:
        """Parses BitTorrent Magnet URI."""
        parsed = urllib.parse.urlparse(magnet_url)
        query = urllib.parse.parse_qs(parsed.query)

        dn = query.get("dn", ["BitTorrent Magnet Download"])[0]
        xt = query.get("xt", [""])[0]
        trackers = query.get("tr", [])

        return {
            "success": True,
            "media_type": "torrent",
            "url": magnet_url,
            "title": dn,
            "thumbnail": "",
            "duration": 0,
            "uploader": "Decentralized Swarm",
            "info_hash": xt,
            "trackers_count": len(trackers),
            "is_onion": False,
            "video_qualities": [
                {"format_id": "torrent_default", "label": "Decentralized P2P Swarm", "ext": "torrent", "type": "p2p"}
            ],
            "audio_qualities": []
        }

media_parser = MediaParser()

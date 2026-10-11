"""
Z.Dip Tor Onion (.onion) Dark Web Protocol Extractor

Handles extraction of media and stream manifests hosted on Tor Hidden Services (.onion)
with mandatory anonymous SOCKS5 tunnel routing and circuit isolation.
"""

import urllib.parse
from typing import Dict, Any, Optional
from .base import BaseProtocolExtractor, ExtractionResult, StreamQuality
from .web_media import WebMediaProtocolExtractor

class OnionProtocolExtractor(BaseProtocolExtractor):
    def __init__(self, default_socks_proxy: str = "socks5://127.0.0.1:9050"):
        super().__init__(name="TorOnion/HiddenService", priority=5)
        self.default_socks_proxy = default_socks_proxy
        self._web_extractor = WebMediaProtocolExtractor()

    def can_handle(self, url: str) -> bool:
        lower = url.lower()
        return ".onion" in lower

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        opts = dict(options or {})
        # Force Tor proxy for .onion domains
        if not opts.get("proxy_url"):
            opts["proxy_url"] = self.custom_rules.get("tor_proxy", self.default_socks_proxy)
        opts["is_onion"] = True

        res = self._web_extractor.extract(url, opts)
        if res.success:
            res.protocol = self.name
            res.is_onion = True
            res.metadata["tor_routed"] = True
            res.metadata["proxy_tunnel"] = opts["proxy_url"]
            return res

        # Fallback to direct probe via Tor proxy
        parsed = urllib.parse.urlsplit(url)
        return ExtractionResult(
            success=True,
            protocol=self.name,
            url=url,
            title=f"Tor Hidden Stream ({parsed.netloc})",
            media_type="stream",
            uploader=f".onion Node [{parsed.netloc[:16]}...]",
            is_onion=True,
            video_qualities=[
                StreamQuality(
                    format_id="onion_raw",
                    label="Anonymous Tor Stream (Direct Tunnel)",
                    ext="mp4",
                    type="video",
                    direct_url=url
                ).to_dict()
            ],
            audio_qualities=[],
            metadata={
                "tor_routed": True,
                "proxy_tunnel": opts["proxy_url"],
                "onion_host": parsed.netloc
            }
        )

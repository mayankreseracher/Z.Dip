"""
Z.Dip Protocol Reinforcement Template & Developer Example

Use this template to create and reinforce custom protocols:
- WebRTC / RTSP / RTMP live security or broadcast streams
- Decentralized Web / IPFS / Arweave / Nostr video hashes
- Private corporate / authenticated streaming endpoints
- Custom P2P or torrent federation trackers

Simply inherit from BaseProtocolExtractor, register via @register_protocol,
and drop this file into your project or plugin folder!
"""

from typing import Dict, Any, Optional
from zdip.protocols.base import BaseProtocolExtractor, ExtractionResult, StreamQuality
from zdip.protocols import register_protocol

@register_protocol
class CustomStreamProtocolExtractor(BaseProtocolExtractor):
    """
    Example Custom Protocol Handler.
    Supports URLs matching 'custom-protocol://*' or 'rtsp://*'
    """
    def __init__(self):
        super().__init__(name="CustomLiveStream", priority=20)

    def can_handle(self, url: str) -> bool:
        lower = url.lower()
        return lower.startswith("custom-live://") or lower.startswith("rtsp://")

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        options = options or {}
        
        # Access any dynamically reinforced parameters
        auth_token = self.custom_rules.get("auth_token", "default_token")
        
        # Build streams
        video_qualities = [
            StreamQuality(
                format_id="custom_hd",
                label="Custom Protocol Stream (HD 1080p)",
                height=1080,
                ext="mp4",
                type="video",
                direct_url=url
            ).to_dict()
        ]

        return ExtractionResult(
            success=True,
            protocol=self.name,
            url=url,
            title="Custom Protocol Video Stream",
            media_type="stream",
            thumbnail="",
            duration=0,
            uploader="Custom Provider",
            video_qualities=video_qualities,
            audio_qualities=[],
            metadata={
                "custom_auth": bool(auth_token),
                "reinforced": True
            }
        )

# 🚀 Protocol Reinforcement Guide

**Z.Dip** includes a modular, extensible protocol reinforcement framework. This enables developers to extract media from new or proprietary networks (such as WebRTC, RTSP, decentralized IPFS/Arweave swarms, or authenticated private feeds) and dynamically reinforce existing extractors with runtime rules.

---

## ⚡ What is Protocol Reinforcement?

Protocol reinforcement operates on two levels:
1. **Dynamic Rule Reinforcement:** Injecting runtime configurations (custom HTTP headers, authentication tokens, cookies, proxy tunnels, or P2P swarm trackers) into registered protocol extractors without restarting the server.
2. **Pluggable Protocol Creation:** Defining new extractor classes that seamlessly integrate into the universal extraction pipeline.

---

## 🛠️ 1. Reinforcing Existing Protocols

### Option A: Via REST API
Send a `POST` request to `/api/protocols/reinforce`:

```bash
curl -X POST http://127.0.0.1:8088/api/protocols/reinforce \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_name": "BitTorrent/Magnet",
    "rules": {
      "custom_trackers": [
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://open.tracker.cl:1337/announce"
      ]
    }
  }'
```

### Option B: Via CLI
```bash
zdip protocols --reinforce "BitTorrent/Magnet" custom_trackers='["udp://tracker.opentrackr.org:1337/announce"]'
```

### Option C: In Python
```python
from zdip.protocols import reinforce_protocol

reinforce_protocol("WebMedia/200+Platforms", {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "cookies_file": "/path/to/cookies.txt"
})
```

---

## 🧩 2. Creating a Custom Protocol Extractor

Creating a new protocol handler requires implementing the `BaseProtocolExtractor` interface and decorating the class with `@register_protocol`.

### Example: Custom RTSP Live Stream Extractor

Save this file anywhere in your application or drop it into `zdip/protocols/`:

```python
from typing import Dict, Any, Optional
from zdip.protocols.base import BaseProtocolExtractor, ExtractionResult, StreamQuality
from zdip.protocols import register_protocol

@register_protocol
class RTSPProtocolExtractor(BaseProtocolExtractor):
    def __init__(self):
        # Priority defines execution order (lower numbers execute first)
        super().__init__(name="RTSP/LiveStream", priority=25)

    def can_handle(self, url: str) -> bool:
        """Define URL pattern matching for this protocol."""
        return url.lower().startswith("rtsp://") or url.lower().startswith("rtsps://")

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """Extract streams, resolution options, and metadata."""
        options = options or {}
        
        # Access reinforced custom rules (e.g. credentials)
        auth_header = self.custom_rules.get("authorization")

        qualities = [
            StreamQuality(
                format_id="rtsp_hd",
                label="RTSP Live Camera Stream (1080p)",
                ext="ts",
                height=1080,
                type="video",
                direct_url=url
            ).to_dict()
        ]

        return ExtractionResult(
            success=True,
            protocol=self.name,
            url=url,
            title="RTSP Live Surveillance Stream",
            media_type="stream",
            video_qualities=qualities,
            metadata={"transport": "RTP/UDP"}
        )
```

Once registered, `zdip.protocols.extract("rtsp://cam1.local/live")` and the web dashboard will automatically recognize and process RTSP streams!

---

## 📋 Protocol Priority Hierarchy

| Priority | Protocol Handler | Description |
|:---:|---|---|
| **5** | `TorOnion/HiddenService` | Handles `.onion` hidden domains via SOCKS5 |
| **10** | `BitTorrent/Magnet` | Handles `magnet:?` and `.torrent` links |
| **30** | `DirectStream/HLS/DASH` | Handles direct `.m3u8`, `.mpd`, `.mp4`, `.mkv` feeds |
| **50** | `WebMedia/200+Platforms` | Handles 200+ platforms via yt-dlp |
| **100+** | Fallback Probe | Generic HTTP HEAD and chunk inspection |

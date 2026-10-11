"""
Unit tests for Z.Dip Protocol Reinforcement System
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from zdip.protocols import (
    registry,
    extract,
    list_protocols,
    reinforce_protocol,
    register_protocol,
    BaseProtocolExtractor,
    ExtractionResult
)

def test_torrent_extraction():
    magnet = "magnet:?xt=urn:btih:3b245504d5f0241cfd17e47a699818b807e62e1e&dn=Big_Buck_Bunny_1080p.mp4&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
    res = extract(magnet)
    assert res.success is True
    assert res.protocol == "BitTorrent/Magnet"
    assert "Big_Buck_Bunny_1080p.mp4" in res.title
    assert res.metadata["info_hash"] == "3B245504D5F0241CFD17E47A699818B807E62E1E"
    assert len(res.video_qualities) > 0
    assert res.video_qualities[0]["type"] == "p2p"

def test_direct_stream_extraction():
    stream_url = "https://example.com/live/stream.m3u8"
    res = extract(stream_url)
    assert res.success is True
    assert res.protocol == "DirectStream/HLS/DASH"
    assert res.media_type == "stream"

def test_onion_extractor():
    onion_url = "http://darkwebvideo76xhyz.onion/watch?v=1234"
    res = extract(onion_url)
    assert res.success is True
    assert res.is_onion is True
    assert res.protocol == "TorOnion/HiddenService"
    assert res.metadata.get("tor_routed") is True

def test_protocol_reinforcement():
    # Reinforce BitTorrent with custom trackers
    ok = reinforce_protocol("BitTorrent/Magnet", {"custom_trackers": ["udp://custom.tracker.org:80/announce"]})
    assert ok is True

    # Test extraction with reinforced rules
    magnet = "magnet:?xt=urn:btih:d2474e86c95b19b8bcfdbb7242f830467d755bc2&dn=LinuxDistro.iso"
    res = extract(magnet)
    assert "udp://custom.tracker.org:80/announce" in res.metadata["trackers"]

def test_dynamic_protocol_registration():
    @register_protocol
    class CustomEchoProtocol(BaseProtocolExtractor):
        def __init__(self):
            super().__init__(name="EchoProtocol", priority=1)

        def can_handle(self, url: str) -> bool:
            return url.startswith("echo://")

        def extract(self, url: str, options=None):
            return ExtractionResult(
                success=True,
                protocol=self.name,
                url=url,
                title=f"Echo: {url[7:]}"
            )

    res = extract("echo://test-video-stream")
    assert res.success is True
    assert res.protocol == "EchoProtocol"
    assert res.title == "Echo: test-video-stream"

if __name__ == "__main__":
    test_torrent_extraction()
    test_direct_stream_extraction()
    test_onion_extractor()
    test_protocol_reinforcement()
    test_dynamic_protocol_registration()
    print("All protocol tests passed successfully!")

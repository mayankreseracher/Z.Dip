"""
Unit tests for Z.Dip Tor Onion Engine
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from zdip.core.tor_engine import tor_engine

def test_tor_detection():
    service = tor_engine.detect_tor_service()
    assert "is_running" in service
    assert "socks_port" in service

def test_onion_url_detection():
    assert tor_engine.is_onion("http://expyuz5wqqfdgah56trsiieabq4ebyikrbtgahwxvgtdqdgyuhpub2yd.onion/") is True
    assert tor_engine.is_onion("https://youtube.com/watch?v=12345") is False

def test_magnet_detection():
    assert tor_engine.is_magnet("magnet:?xt=urn:btih:1234567890abcdef") is True
    assert tor_engine.is_magnet("https://example.com/video.mp4") is False

if __name__ == "__main__":
    test_tor_detection()
    test_onion_url_detection()
    test_magnet_detection()
    print("Tor Engine tests passed successfully!")

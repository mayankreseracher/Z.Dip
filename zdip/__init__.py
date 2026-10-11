"""
Z.Dip - Sovereign Media Extraction, BitTorrent & Multi-Cloud Privacy Engine

Extracts media from torrents and 200+ platforms and stores on cloud storage
with custom support for reinforcing new protocols.
"""

__version__ = "1.2.0"
__author__ = "Mayank (mayankreseracher)"

from .protocols import extract, register_protocol, list_protocols, reinforce_protocol
from .core.bclone_bridge import bclone
from .core.tor_engine import tor_engine
from .core.download_manager import download_manager
from .config import APP_CONFIG

__all__ = [
    "extract",
    "register_protocol",
    "list_protocols",
    "reinforce_protocol",
    "bclone",
    "tor_engine",
    "download_manager",
    "APP_CONFIG",
]

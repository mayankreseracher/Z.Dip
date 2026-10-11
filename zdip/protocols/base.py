"""
Z.Dip Protocol Reinforcement Engine - Base Protocol Definition

Provides the abstract base class and contract for all protocol extractors.
Enables pluggable extraction rules and dynamic protocol reinforcement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class StreamQuality:
    format_id: str
    label: str
    ext: str = "mp4"
    type: str = "video" # "video", "audio", "file", "p2p"
    height: Optional[int] = None
    width: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    direct_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format_id": self.format_id,
            "label": self.label,
            "ext": self.ext,
            "type": self.type,
            "height": self.height,
            "width": self.width,
            "fps": self.fps,
            "bitrate": self.bitrate,
            "vcodec": self.vcodec,
            "acodec": self.acodec,
            "filesize": self.filesize,
            "direct_url": self.direct_url,
        }

@dataclass
class ExtractionResult:
    success: bool
    protocol: str
    url: str
    title: str = "Unknown Title"
    media_type: str = "video" # "video", "audio", "torrent", "stream", "direct_file"
    thumbnail: str = ""
    duration: int = 0
    uploader: str = "Unknown"
    is_onion: bool = False
    video_qualities: List[Dict[str, Any]] = field(default_factory=list)
    audio_qualities: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "protocol": self.protocol,
            "url": self.url,
            "title": self.title,
            "media_type": self.media_type,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "uploader": self.uploader,
            "is_onion": self.is_onion,
            "video_qualities": self.video_qualities,
            "audio_qualities": self.audio_qualities,
            "metadata": self.metadata,
            "error": self.error,
        }

class BaseProtocolExtractor(ABC):
    """
    Abstract Base Class for Z.Dip Protocol Extractors.
    
    Implement this class to add extraction capabilities for new network protocols,
    streaming technologies, decentralized networks, or proprietary video APIs.
    """
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
        self.custom_rules: Dict[str, Any] = {}

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True if this extractor can process the given URL or URI."""
        pass

    @abstractmethod
    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """
        Analyze and extract video/audio streams, formats, and metadata.
        
        Args:
            url: Target URL, URI, magnet link, or protocol identifier.
            options: Extraction options (use_tor, custom_proxy, timeout, credentials, etc.)
        """
        pass

    def reinforce(self, rules: Dict[str, Any]) -> None:
        """
        Dynamically reinforce the protocol extractor with custom parameters,
        custom regexes, headers, authentication tokens, or proxy rules.
        """
        self.custom_rules.update(rules)

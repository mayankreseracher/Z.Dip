"""
Z.Dip Protocol Reinforcement System

Manages the discovery, registration, ordering, and execution of media protocols
(Torrents, 200+ Web Platforms, Direct Streams, Onion Hidden Services, Custom Protocols).
"""

import logging
from typing import List, Dict, Any, Type, Optional
from .base import BaseProtocolExtractor, ExtractionResult, StreamQuality
from .torrent import TorrentProtocolExtractor
from .web_media import WebMediaProtocolExtractor
from .direct_stream import DirectStreamProtocolExtractor
from .onion import OnionProtocolExtractor

logger = logging.getLogger("zdip.protocols")

class ProtocolRegistry:
    def __init__(self):
        self._extractors: List[BaseProtocolExtractor] = []

    def register(self, extractor: BaseProtocolExtractor) -> None:
        """Register an instantiated protocol extractor."""
        self._extractors.append(extractor)
        # Sort extractors by priority (lower number = higher precedence)
        self._extractors.sort(key=lambda x: x.priority)
        logger.debug(f"Registered protocol extractor: {extractor.name} (Priority {extractor.priority})")

    def register_class(self, cls: Type[BaseProtocolExtractor]) -> Type[BaseProtocolExtractor]:
        """Class decorator for registering custom protocol extractors."""
        instance = cls()
        self.register(instance)
        return cls

    def list_protocols(self) -> List[Dict[str, Any]]:
        """List all currently active protocols and their priority."""
        return [
            {
                "name": ext.name,
                "priority": ext.priority,
                "custom_rules_count": len(ext.custom_rules),
                "rules": ext.custom_rules
            }
            for ext in self._extractors
        ]

    def get_handler(self, url: str) -> Optional[BaseProtocolExtractor]:
        """Find the first matching protocol extractor for the given URL/URI."""
        for ext in self._extractors:
            try:
                if ext.can_handle(url):
                    return ext
            except Exception as e:
                logger.warning(f"Error checking {ext.name}.can_handle: {e}")
        return None

    def reinforce(self, protocol_name: str, rules: Dict[str, Any]) -> bool:
        """
        Dynamically reinforce an existing protocol extractor with custom rules,
        credentials, headers, or proxies.
        """
        for ext in self._extractors:
            if ext.name.lower() == protocol_name.lower():
                ext.reinforce(rules)
                logger.info(f"Protocol '{ext.name}' reinforced with {len(rules)} rules.")
                return True
        return False

    def extract(self, url: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """
        Extract video streams, torrent metadata, or audio from the given URL.
        Dispatches automatically to the appropriate registered protocol extractor.
        """
        options = options or {}
        handler = self.get_handler(url)

        if handler:
            logger.info(f"Dispatching URL to protocol extractor: {handler.name}")
            return handler.extract(url, options)

        # Fallback to direct stream extractor
        fallback = DirectStreamProtocolExtractor()
        logger.info(f"No specific protocol matched. Falling back to direct stream probe.")
        return fallback.extract(url, options)

# Global Registry Instance
registry = ProtocolRegistry()

# Register Built-in Protocol Extractors
registry.register(TorrentProtocolExtractor())
registry.register(OnionProtocolExtractor())
registry.register(WebMediaProtocolExtractor())
registry.register(DirectStreamProtocolExtractor())

# Export convenience functions
register_protocol = registry.register_class
extract = registry.extract
reinforce_protocol = registry.reinforce
list_protocols = registry.list_protocols

__all__ = [
    "BaseProtocolExtractor",
    "ExtractionResult",
    "StreamQuality",
    "TorrentProtocolExtractor",
    "WebMediaProtocolExtractor",
    "DirectStreamProtocolExtractor",
    "OnionProtocolExtractor",
    "ProtocolRegistry",
    "registry",
    "register_protocol",
    "extract",
    "reinforce_protocol",
    "list_protocols",
]

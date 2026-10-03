import socket
import logging
import time
from typing import Dict, Any, Optional
import urllib.request
import json
from .config import TOR_CONFIG, DEFAULT_TOR_SOCKS_PORT, TOR_ALT_SOCKS_PORT, DEFAULT_TOR_CONTROL_PORT, TOR_ALT_CONTROL_PORT

logger = logging.getLogger("tor_engine")

class TorEngine:
    def __init__(self):
        self.config = dict(TOR_CONFIG)
        self.active_socks_port: Optional[int] = None
        self.active_control_port: Optional[int] = None
        self.last_identity_check: Optional[Dict[str, Any]] = None
        self.last_check_time: float = 0

    def check_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if TCP port is listening."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    def detect_tor_service(self) -> Dict[str, Any]:
        """Auto-detect active Tor SOCKS5 and Control ports."""
        host = self.config.get("socks_host", "127.0.0.1")
        
        # Test default port (9050) then Tor Browser port (9150)
        ports_to_check = [
            (self.config.get("socks_port", DEFAULT_TOR_SOCKS_PORT), self.config.get("control_port", DEFAULT_TOR_CONTROL_PORT)),
            (TOR_ALT_SOCKS_PORT, TOR_ALT_CONTROL_PORT)
        ]
        
        found_socks = None
        found_control = None

        for s_port, c_port in ports_to_check:
            if self.check_port_open(host, s_port):
                found_socks = s_port
                if self.check_port_open(host, c_port):
                    found_control = c_port
                break

        self.active_socks_port = found_socks
        self.active_control_port = found_control

        return {
            "is_running": found_socks is not None,
            "host": host,
            "socks_port": found_socks,
            "control_port": found_control,
            "socks_proxy_url": f"socks5://{host}:{found_socks}" if found_socks else None
        }

    def get_proxy_url(self) -> Optional[str]:
        """Returns active SOCKS5 proxy URL if available."""
        if not self.active_socks_port:
            self.detect_tor_service()
        if self.active_socks_port:
            return f"socks5://{self.config.get('socks_host', '127.0.0.1')}:{self.active_socks_port}"
        return None

    def is_onion(self, url: str) -> bool:
        """Check if URL targets a Tor .onion hidden service."""
        return ".onion" in url.lower()

    def is_magnet(self, url: str) -> bool:
        """Check if URL is a BitTorrent magnet link."""
        return url.lower().startswith("magnet:?")

    def get_network_identity(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Compare clearnet public IP vs Tor exit IP.
        """
        now = time.time()
        if not force_refresh and self.last_identity_check and (now - self.last_check_time < 30):
            return self.last_identity_check

        tor_status = self.detect_tor_service()
        clearnet_ip = "Unknown"
        tor_exit_ip = None
        is_tor_verified = False

        # 1. Fetch Clearnet IP
        try:
            req = urllib.request.Request(
                "https://api.ipify.org?format=json",
                headers={"User-Agent": "Zytor-Media-Engine/1.2"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode("utf-8"))
                clearnet_ip = data.get("ip", "Unknown")
        except Exception as e:
            logger.debug(f"Clearnet IP check error: {e}")

        # 2. Fetch Tor Exit IP (if Tor SOCKS5 is active)
        if tor_status["is_running"]:
            try:
                import socks
                import urllib.request as tor_urllib

                # Build socks opener
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler({
                        "http": f"socks5h://{tor_status['host']}:{tor_status['socks_port']}",
                        "https": f"socks5h://{tor_status['host']}:{tor_status['socks_port']}",
                    })
                )
                req = urllib.request.Request(
                    "https://check.torproject.org/api/ip",
                    headers={"User-Agent": "Zytor-Media-Engine/1.2"}
                )
                with opener.open(req, timeout=8) as res:
                    tor_data = json.loads(res.read().decode("utf-8"))
                    tor_exit_ip = tor_data.get("IP")
                    is_tor_verified = tor_data.get("IsTor", False)
            except Exception as e:
                logger.debug(f"Tor exit IP check error: {e}")

        result = {
            "tor_running": tor_status["is_running"],
            "socks_proxy": tor_status["socks_proxy_url"],
            "control_port": tor_status["control_port"],
            "clearnet_ip": clearnet_ip,
            "tor_exit_ip": tor_exit_ip,
            "is_tor_verified": is_tor_verified,
            "onion_routing_ready": tor_status["is_running"]
        }

        self.last_identity_check = result
        self.last_check_time = now
        return result

    def rotate_circuit(self) -> Dict[str, Any]:
        """
        Signals Tor controller to generate a new identity/circuit (NEWNYM).
        """
        det = self.detect_tor_service()
        control_port = det.get("control_port")
        if not control_port:
            return {"success": False, "message": "Tor Control Port is not active or accessible (typically 9051 or 9151)."}

        try:
            from stem import Signal
            from stem.control import Controller

            with Controller.from_port(port=control_port) as controller:
                pwd = self.config.get("control_password", "")
                if pwd:
                    controller.authenticate(password=pwd)
                else:
                    controller.authenticate() # blank/cookie auth

                controller.signal(Signal.NEWNYM)
                time.sleep(0.5)

            # Clear cache and recheck IP
            self.last_identity_check = None
            new_id = self.get_network_identity(force_refresh=True)

            return {
                "success": True,
                "message": "Tor circuit rotated successfully. New identity acquired.",
                "new_exit_ip": new_id.get("tor_exit_ip")
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Circuit rotation failed: {str(e)}"
            }

tor_engine = TorEngine()

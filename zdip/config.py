"""
Z.Dip Configuration & Toolchain Discovery Engine

Automatically discovers and manages runtime dependencies (bclone, yt-dlp, aria2c, Tor)
across Windows, Linux, and macOS environments without hardcoded user directories.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any

# Root Z.Dip Engine Directory
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

# Persistent Storage Directories
CONFIG_DIR = PROJECT_ROOT / "config"
DOWNLOADS_DIR = PROJECT_ROOT / "downloads"
BIN_DIR = PROJECT_ROOT / "bin"
WEB_DIR = PACKAGE_DIR / "web"

# Ensure runtime directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def resolve_binary(binary_name: str, env_var: str) -> Path:
    """
    Search for executable binary in priority order:
    1. Environment variable override
    2. Local bin/ directory in project
    3. System PATH
    """
    # 1. Environment variable
    if env_var in os.environ and os.environ[env_var]:
        candidate = Path(os.environ[env_var])
        if candidate.exists():
            return candidate

    # 2. Local project bin/ directory
    is_windows = sys.platform.startswith("win")
    exts = [".exe", ".cmd", ".bat"] if is_windows else ["", ".sh"]

    for ext in exts:
        local_cand = BIN_DIR / f"{binary_name}{ext}"
        if local_cand.exists():
            return local_cand
        
        # Check parent engine/bin if present
        engine_cand = PROJECT_ROOT / "engine" / "bin" / f"{binary_name}{ext}"
        if engine_cand.exists():
            return engine_cand

    # 3. System PATH
    system_path = shutil.which(binary_name)
    if system_path:
        return Path(system_path)

    # Default fallback to expected local name
    return BIN_DIR / (f"{binary_name}.exe" if is_windows else binary_name)

# Toolchain Executables
BCLONE_EXE = resolve_binary("bclone", "ZDIP_BCLONE_BIN")
YTDLP_EXE = resolve_binary("yt-dlp", "ZDIP_YTDLP_BIN")
ARIA2C_EXE = resolve_binary("aria2c", "ZDIP_ARIA2C_BIN")

# Persistent bclone Configuration
BCLONE_CONF = CONFIG_DIR / "bclone.conf"

# Tor SOCKS5 and Control Port defaults
DEFAULT_TOR_SOCKS_PORT = int(os.environ.get("TOR_SOCKS_PORT", 9050))
TOR_ALT_SOCKS_PORT = 9150
DEFAULT_TOR_CONTROL_PORT = int(os.environ.get("TOR_CONTROL_PORT", 9051))
TOR_ALT_CONTROL_PORT = 9151

TOR_CONFIG: Dict[str, Any] = {
    "enabled": False,
    "socks_host": os.environ.get("TOR_HOST", "127.0.0.1"),
    "socks_port": DEFAULT_TOR_SOCKS_PORT,
    "control_port": DEFAULT_TOR_CONTROL_PORT,
    "control_password": os.environ.get("TOR_CONTROL_PASSWORD", ""),
    "bridge_mode": "auto",
    "circuit_isolation": True,
    "auto_rotate_minutes": 10
}

TURBOBOLT_CONFIG: Dict[str, Any] = {
    "default_segments": 16,
    "max_segments": 64,
    "max_concurrent_connections": 32,
    "chunk_size_mb": 10,
    "auto_retry_count": 5,
    "socket_timeout_sec": 30
}

APP_CONFIG: Dict[str, Any] = {
    "app_name": "Z.Dip Sovereign Engine",
    "version": "1.2.0",
    "host": os.environ.get("ZDIP_HOST", "127.0.0.1"),
    "port": int(os.environ.get("ZDIP_PORT", 8088)),
    "downloads_dir": str(DOWNLOADS_DIR),
    "config_dir": str(CONFIG_DIR),
    "bclone_conf": str(BCLONE_CONF),
}

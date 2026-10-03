import os
from pathlib import Path

# Base Paths
ENGINE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = ENGINE_DIR / "bin"
CONFIG_DIR = ENGINE_DIR / "config"
DOWNLOADS_DIR = ENGINE_DIR / "downloads"
WEB_DIR = ENGINE_DIR / "web"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Binaries
BCLONE_EXE = BIN_DIR / "bclone.exe"
YTDLP_EXE = BIN_DIR / "yt-dlp.exe"
BCLONE_CONF = CONFIG_DIR / "bclone.conf"

# Tor & Privacy defaults
DEFAULT_TOR_SOCKS_PORT = 9050
DEFAULT_TOR_CONTROL_PORT = 9051
TOR_ALT_SOCKS_PORT = 9150  # Common for Tor Browser bundle
TOR_ALT_CONTROL_PORT = 9151

TOR_CONFIG = {
    "enabled_by_default": False,
    "socks_host": "127.0.0.1",
    "socks_port": DEFAULT_TOR_SOCKS_PORT,
    "control_port": DEFAULT_TOR_CONTROL_PORT,
    "control_password": "",
    "auto_rotate_circuits": True,
}

# TurboBolt Defaults
TURBOBOLT_CONFIG = {
    "default_segments": 16,
    "max_segments": 64,
    "min_chunk_size_mb": 2,
    "max_connections_per_host": 32,
    "unlimited_speed": True,
    "max_speed_kbs": 0,  # 0 = uncapped
    "retry_attempts": 5,
}

# Default App Settings
APP_CONFIG = {
    "port": 8088,
    "host": "0.0.0.0",
    "default_storage_mode": "local",  # "local", "sync_copy", "direct_stream"
    "default_remote": "",
    "default_remote_path": "ZytorMedia",
    "delete_local_after_sync": False,
    "encrypt_by_default": False,
}

# 🖥️ Z.Dip Desktop & Server Engine

This directory provides backward-compatible launchers and legacy entrypoints for the Z.Dip core engine.

---

## 🚀 Quick Start

### Option 1: Using the Batch Launcher (Windows)
Double-click `start_zytor.bat` (or root `start_zdip.bat`). The launcher automatically detects Python 3.10+ and starts the engine on `http://127.0.0.1:8088`.

### Option 2: Command Line
```bash
# From repository root:
python -m zdip.server
```
Or from this directory:
```bash
python server.py
```

Then navigate to `http://127.0.0.1:8088` to open the Dark OLED Web Dashboard.

---

## 📂 Architecture Mapping

All core engine logic has been modernized and unified into the top-level `zdip/` package:
- **`zdip.protocols`**: BitTorrent, 200+ Video Platforms, Direct Streams, Tor Onion routing, and Custom Protocol Reinforcement.
- **`zdip.core.turbobolt`**: 64-segment parallel multi-threaded downloader.
- **`zdip.core.bclone_bridge`**: Multi-cloud storage bridge (Terabox, Google Drive, OneDrive, S3, WebDAV) and AES-256 Crypt Vaults.
- **`zdip.core.tor_engine`**: Tor proxy detection, SOCKS5 routing, and circuit identity rotator.
- **`zdip.server`**: Asynchronous FastAPI and WebSocket telemetry server.
- **`zdip.web`**: Glassmorphic dark dashboard UI.

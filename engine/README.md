# Zytor Sovereign • Unified Media Downloader & Cloud Privacy Engine

A powerful, privacy-first evolution of **[Zytor](https://github.com/ImKKingshuk/Zytor)** integrating cloud storage and zero-knowledge encryption powered by **[bclone](https://github.com/BenjiThatFoxGuy/bclone)** and native **Tor Onion Routing / Torrent** downloading.

---

## ⚡ Key Innovations

### 1. TurboBolt 64-Segment Engine
- Extreme parallelization supporting up to **64 segments** and **32 concurrent connections**.
- Universal extraction across 300+ streaming sites (YouTube, Instagram, TikTok, Twitter/X, Reddit, Twitch, Vimeo, SoundCloud).
- Full resolution range: `8K • 4K • 2K • 1080p • 720p • 480p • Audio (FLAC, MP3 320k, WAV, OPUS)`.

### 2. bclone Multi-Cloud Storage & Zero-Disk Streaming
Directly integrates **bclone** (the enhanced fork of rclone) with specialized backends:
- **bclone Exclusive Backends**: `Terabox`, `AList`, `TelDrive` (unlimited Telegram storage), `gotohp` (unofficial Google Photos), `AllDebrid`.
- **Standard Cloud Remotes**: `Google Drive`, `Microsoft OneDrive`, `Dropbox`, `Mega.nz`, `Amazon S3`, `Cloudflare R2`, `MinIO`, `WebDAV (Nextcloud)`, `SFTP`.
- **3 Flexible Storage Pathways**:
  1. **Local Storage**: Saved directly to local disk `downloads/`.
  2. **Staged Cloud Sync/Copy**: Downloads locally at maximum TurboBolt speed, then automatically uploads to cloud remote (with optional local deletion).
  3. **Direct-to-Cloud Zero-Disk Streaming (`rcat`)**: Streams network media directly through bclone stdin pipe into cloud storage—**zero bytes consumed on physical local disk**.

### 3. Client-Side AES-256 Zero-Knowledge Crypt Vaults
- Wrap any cloud provider (e.g. Terabox, Google Drive, S3, WebDAV) with an encrypted virtual remote.
- Encrypts file contents (AES-256-GCM) and directory/file names before they leave your machine.
- Cloud providers store only scrambled ciphertext.

### 4. Native Tor Onion Routing & Anonymity Center
- Integrated SOCKS5 onion proxy routing (`socks5://127.0.0.1:9050` / `9150`).
- Resolves and downloads `.onion` hidden services and bypasses geo-blocking/ISP censorship.
- Identity rotation button sending `SIGNAL NEWNYM` to switch Tor circuits.
- Decentralized BitTorrent / Magnet link resolving.

---

## 🚀 Quick Start

### Windows
Double-click `start_zytor.bat` or run:
```powershell
cd "zytor-engine"
& "C:\Users\Mayank\AppData\Local\Programs\Python\Python312\python.exe" server.py
```
Then open `http://127.0.0.1:8088` in your browser.

---

## 📂 Architecture Overview

```
zytor-engine/
├── bin/
│   ├── bclone.exe      # Official BenjiThatFoxGuy/bclone binary (v1.74.0)
│   └── yt-dlp.exe      # Media extraction engine
├── config/
│   └── bclone.conf     # Persistent bclone remote definitions & Crypt vaults
├── core/
│   ├── bclone_bridge.py # Python wrapper for bclone commands & rcat pipe
│   ├── config.py       # Configuration & binary locations
│   ├── download_manager.py # Job queue & WebSocket broadcaster
│   ├── media_parser.py # URL inspector & quality extractor
│   ├── tor_engine.py   # Tor detection, circuit rotator & SOCKS5 client
│   └── turbobolt.py    # Multi-segment parallel downloader & cloud streamer
├── downloads/          # Local download destination folder
├── web/
│   ├── app.js          # Reactive frontend controller & WebSocket client
│   ├── index.html      # Zytor OLED dark UI dashboard
│   └── styles.css      # Glassmorphic Zytor aesthetics
├── server.py           # FastAPI + WebSocket backend server
└── start_zytor.bat     # Windows 1-click startup launcher
```

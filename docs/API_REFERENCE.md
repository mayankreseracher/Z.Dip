# 📡 Z.Dip REST API & WebSocket Reference

The Z.Dip backend exposes an asynchronous REST and WebSocket API on `http://127.0.0.1:8088`.

---

## 🔍 Media & Protocol Endpoints

### 1. Extract Media Metadata & Streams
`POST /api/analyze`

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "use_tor": false,
  "custom_proxy": null
}
```

**Response:**
```json
{
  "success": true,
  "protocol": "WebMedia/200+Platforms",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "media_type": "stream",
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "duration": 213,
  "uploader": "Rick Astley",
  "is_onion": false,
  "video_qualities": [
    {
      "format_id": "137+140",
      "label": "1080p FHD",
      "height": 1080,
      "ext": "mp4",
      "fps": 30.0,
      "filesize": 78241902
    }
  ],
  "audio_qualities": [
    {
      "format_id": "140",
      "label": "128 kbps (M4A)",
      "bitrate": 128,
      "ext": "m4a"
    }
  ]
}
```

### 2. List Registered Protocols
`GET /api/protocols`

**Response:**
```json
{
  "success": true,
  "protocols": [
    {"name": "TorOnion/HiddenService", "priority": 5, "custom_rules_count": 0},
    {"name": "BitTorrent/Magnet", "priority": 10, "custom_rules_count": 0},
    {"name": "DirectStream/HLS/DASH", "priority": 30, "custom_rules_count": 0},
    {"name": "WebMedia/200+Platforms", "priority": 50, "custom_rules_count": 0}
  ]
}
```

### 3. Reinforce Protocol Extractor
`POST /api/protocols/reinforce`

**Request Body:**
```json
{
  "protocol_name": "BitTorrent/Magnet",
  "rules": {
    "custom_trackers": ["udp://tracker.opentrackr.org:1337/announce"]
  }
}
```

---

## ⚡ Download Engine Endpoints

### 4. Create Download Task
`POST /api/download`

**Request Body:**
```json
{
  "url": "https://example.com/video.mp4",
  "title": "MyVideo",
  "format_id": "best",
  "is_audio_only": false,
  "storage_mode": "sync_copy",
  "dest_remote": "terabox",
  "dest_folder": "ZytorMedia",
  "delete_local_after_sync": true,
  "use_tor": false,
  "segments": 16
}
```

### 5. List Download Tasks
`GET /api/jobs`

### 6. Cancel Download Task
`DELETE /api/jobs/{job_id}`

### 7. Clear Inactive Jobs
`POST /api/jobs/clear`

---

## ☁️ bclone Cloud Storage Endpoints

### 8. List Remotes & Supported Backends
`GET /api/bclone/remotes`

### 9. Create Cloud Remote
`POST /api/bclone/remotes`

### 10. Deploy AES-256 Crypt Vault
`POST /api/bclone/crypt`

**Request Body:**
```json
{
  "vault_name": "encrypted_vault",
  "base_remote": "terabox",
  "base_path": "EncryptedFolder",
  "password": "strong_passphrase",
  "salt": "optional_salt",
  "filename_encryption": "standard",
  "directory_name_encryption": true
}
```

### 11. Browse Remote Files
`GET /api/bclone/files?remote=encrypted_vault&path=`

---

## 🧅 Tor Network Endpoints

### 12. Check Tor Identity & Anonymity
`GET /api/tor/status?refresh=true`

### 13. Rotate Tor Circuit (NEWNYM)
`POST /api/tor/newnym`

---

## 🔴 WebSocket Telemetry

Connect to `ws://127.0.0.1:8088/ws` to receive live download progress events:

```json
{
  "type": "job_update",
  "data": {
    "job_id": "4a7b8c9d",
    "status": "DOWNLOADING",
    "progress": 54.2,
    "speed": "14.5 MB/s",
    "eta": "00:32",
    "downloaded_bytes": 145000000,
    "total_bytes": 268000000
  }
}
```

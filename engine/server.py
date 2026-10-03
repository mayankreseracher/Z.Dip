import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure parent directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import APP_CONFIG, DOWNLOADS_DIR, WEB_DIR
from core.bclone_bridge import bclone
from core.tor_engine import tor_engine
from core.media_parser import media_parser
from core.download_manager import download_manager

app = FastAPI(title="Zytor Sovereign Engine", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_websockets: List[WebSocket] = []

def ws_broadcaster(data: Dict[str, Any]):
    """Push updates to all active WebSocket clients."""
    if not active_websockets:
        return
    msg = json.dumps({"type": "job_update", "data": data})
    loop = asyncio.get_event_loop()
    for ws in list(active_websockets):
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(msg), loop)
        except Exception:
            pass

download_manager.register_listener(ws_broadcaster)

# ----------------- Models -----------------
class AnalyzeRequest(BaseModel):
    url: str
    use_tor: bool = False
    custom_proxy: Optional[str] = None

class DownloadRequest(BaseModel):
    url: str
    title: str
    format_id: str = "best"
    is_audio_only: bool = False
    audio_format: str = "mp3"
    storage_mode: str = "local" # local, sync_copy, direct_stream
    dest_remote: str = ""
    dest_folder: str = "ZytorMedia"
    delete_local_after_sync: bool = False
    use_tor: bool = False
    segments: int = 16
    embed_metadata: bool = True
    embed_thumbnail: bool = True
    embed_subtitles: bool = False
    subtitle_lang: str = "en.*"
    video_codec: str = "auto"
    media_type: str = "video"

class CreateRemoteRequest(BaseModel):
    name: str
    backend_type: str
    parameters: Dict[str, str]

class RawConfigRequest(BaseModel):
    config_text: str

class CreateCryptVaultRequest(BaseModel):
    vault_name: str
    base_remote: str
    base_path: str = "EncryptedVault"
    password: str = ""
    salt: str = ""
    filename_encryption: str = "standard"
    directory_name_encryption: bool = True

class TestRemoteRequest(BaseModel):
    remote_name: str

# ----------------- REST Endpoints -----------------

@app.post("/api/analyze")
async def analyze_url(req: AnalyzeRequest):
    """Analyze URL using yt-dlp / Tor / probe."""
    res = await asyncio.to_thread(media_parser.analyze_url, req.url, req.use_tor, req.custom_proxy)
    return res

@app.get("/api/downloads")
async def get_downloads():
    """List all download jobs."""
    return download_manager.list_jobs()

@app.post("/api/downloads")
async def start_download(req: DownloadRequest):
    """Start a new TurboBolt download job."""
    job = download_manager.create_job(
        url=req.url,
        title=req.title,
        format_id=req.format_id,
        is_audio_only=req.is_audio_only,
        audio_format=req.audio_format,
        storage_mode=req.storage_mode,
        dest_remote=req.dest_remote,
        dest_folder=req.dest_folder,
        delete_local_after_sync=req.delete_local_after_sync,
        use_tor=req.use_tor,
        segments=req.segments,
        embed_metadata=req.embed_metadata,
        embed_thumbnail=req.embed_thumbnail,
        embed_subtitles=req.embed_subtitles,
        subtitle_lang=req.subtitle_lang,
        video_codec=req.video_codec,
        media_type=req.media_type
    )
    return job

@app.delete("/api/downloads/{job_id}")
async def cancel_download(job_id: str):
    """Cancel an active download job."""
    success = download_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"success": True, "job_id": job_id}

@app.post("/api/downloads/clear")
async def clear_completed_downloads():
    """Clear finished or cancelled jobs from history."""
    download_manager.clear_completed()
    return {"success": True}

# --- bclone Cloud Storage Endpoints ---

@app.get("/api/remotes")
async def list_remotes():
    """List all configured bclone cloud remotes."""
    remotes = await asyncio.to_thread(bclone.list_remotes)
    return remotes

@app.get("/api/remotes/backends")
async def list_backends():
    """List supported cloud storage backends (Terabox, Alist, Teldrive, gotohp, etc.)."""
    return bclone.get_supported_backends()

@app.post("/api/remotes")
async def create_remote(req: CreateRemoteRequest):
    """Create or configure a new bclone remote."""
    res = await asyncio.to_thread(bclone.create_remote, req.name, req.backend_type, req.parameters)
    return res

@app.delete("/api/remotes/{name}")
async def delete_remote(name: str):
    """Delete a bclone remote."""
    res = await asyncio.to_thread(bclone.delete_remote, name)
    return res

@app.post("/api/remotes/test")
async def test_remote(req: TestRemoteRequest):
    """Test connection to cloud remote."""
    res = await asyncio.to_thread(bclone.test_connection, req.remote_name)
    return res

@app.post("/api/remotes/crypt")
async def create_crypt_vault(req: CreateCryptVaultRequest):
    """Create a client-side zero-knowledge encrypted vault remote."""
    res = await asyncio.to_thread(
        bclone.create_crypt_vault,
        vault_name=req.vault_name,
        base_remote=req.base_remote,
        base_path=req.base_path,
        password=req.password,
        salt=req.salt,
        filename_encryption=req.filename_encryption,
        directory_name_encryption=req.directory_name_encryption
    )
    return res

@app.post("/api/remotes/import-system")
async def import_system_remotes():
    """Import existing rclone remotes from Windows APPDATA or Linux user profile."""
    res = await asyncio.to_thread(bclone.import_system_config)
    return res

@app.get("/api/remotes/raw")
async def get_raw_config():
    """Get raw bclone.conf content."""
    text = await asyncio.to_thread(bclone.get_raw_config)
    return {"config_text": text}

@app.post("/api/remotes/raw")
async def save_raw_config(req: RawConfigRequest):
    """Save raw bclone.conf content."""
    res = await asyncio.to_thread(bclone.save_raw_config, req.config_text)
    return res

@app.get("/api/remotes/{name}/files")
async def list_remote_files(name: str, path: str = ""):
    """Browse files inside a cloud remote."""
    target = f"{name}:{path}"
    files = await asyncio.to_thread(bclone.list_files, target)
    return files

# --- Tor & Privacy Endpoints ---

@app.get("/api/tor/status")
async def get_tor_status(refresh: bool = False):
    """Check Tor daemon, SOCKS5 tunnel, and compare clearnet vs Tor exit IP."""
    status = await asyncio.to_thread(tor_engine.get_network_identity, refresh)
    return status

@app.post("/api/tor/rotate")
async def rotate_tor_circuit():
    """Rotate Tor circuit and acquire new identity."""
    res = await asyncio.to_thread(tor_engine.rotate_circuit)
    return res

# --- System & Config ---

@app.get("/api/config")
async def get_app_config():
    """Get system and default configuration."""
    return {
        "app": APP_CONFIG,
        "downloads_dir": str(DOWNLOADS_DIR),
        "bclone_version": "1.74.0 (bclone fork)",
        "turbobolt_max_segments": 64
    }

# --- WebSocket for Real-time Telemetry ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        # Send initial state
        initial_data = json.dumps({
            "type": "init",
            "jobs": download_manager.list_jobs()
        })
        await websocket.send_text(initial_data)

        # Keep listening for pings
        while True:
            msg = await websocket.receive_text()
            # Echo ping
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
    except Exception:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

# --- Mount Web Frontend ---
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=APP_CONFIG["host"], port=APP_CONFIG["port"])

"""
Z.Dip Sovereign Engine - FastAPI & WebSocket Asynchronous Server

Provides full REST APIs, WebSocket real-time event broadcasting,
protocol reinforcement endpoints, multi-cloud storage management,
and Tor anonymity controls.
"""

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

from zdip.config import APP_CONFIG, DOWNLOADS_DIR, WEB_DIR
from zdip.core.bclone_bridge import bclone
from zdip.core.tor_engine import tor_engine
from zdip.core.download_manager import download_manager
from zdip.protocols import extract, reinforce_protocol, list_protocols

app = FastAPI(title="Z.Dip Sovereign Engine", version="1.2.0")

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

# ----------------- Request Models -----------------

class AnalyzeRequest(BaseModel):
    url: str
    use_tor: bool = False
    custom_proxy: Optional[str] = None

class ReinforceProtocolRequest(BaseModel):
    protocol_name: str
    rules: Dict[str, Any]

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
    """
    Extract media streams, BitTorrent metadata, or direct streams
    using the Z.Dip Protocol Reinforcement Pipeline.
    """
    proxy_url = req.custom_proxy or (tor_engine.get_proxy_url() if req.use_tor else None)
    opts = {
        "use_tor": req.use_tor,
        "proxy_url": proxy_url,
        "is_onion": tor_engine.is_onion(req.url)
    }
    res = await asyncio.to_thread(extract, req.url, opts)
    return res.to_dict()

@app.get("/api/protocols")
async def get_protocols():
    """List all registered protocol extractors and active reinforcement rules."""
    return {"success": True, "protocols": list_protocols()}

@app.post("/api/protocols/reinforce")
async def reinforce_protocol_endpoint(req: ReinforceProtocolRequest):
    """Reinforce an existing protocol extractor with custom rules."""
    success = reinforce_protocol(req.protocol_name, req.rules)
    if not success:
        raise HTTPException(status_code=404, detail=f"Protocol '{req.protocol_name}' not found.")
    return {"success": True, "message": f"Protocol '{req.protocol_name}' reinforced successfully."}

@app.post("/api/download")
async def start_download(req: DownloadRequest):
    """Create and start a TurboBolt download or direct cloud stream."""
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
    return {"success": True, "job": job}

@app.get("/api/jobs")
async def list_jobs():
    """List all active, pending, and completed download tasks."""
    return {"success": True, "jobs": download_manager.list_jobs()}

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel an active download task."""
    ok = download_manager.cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found or already stopped")
    return {"success": True, "job_id": job_id}

@app.post("/api/jobs/clear")
async def clear_completed():
    """Clear completed and failed jobs from queue."""
    download_manager.clear_completed()
    return {"success": True}

# ----------------- bclone Cloud Remotes Endpoints -----------------

@app.get("/api/bclone/remotes")
async def get_remotes():
    """List all configured bclone remotes and crypt vaults."""
    remotes = await asyncio.to_thread(bclone.list_remotes)
    backends = bclone.get_supported_backends()
    return {
        "success": True,
        "remotes": remotes,
        "supported_backends": backends,
        "config_path": bclone.conf
    }

@app.post("/api/bclone/remotes")
async def create_remote(req: CreateRemoteRequest):
    """Create a new standard cloud storage remote."""
    res = await asyncio.to_thread(bclone.create_remote, req.name, req.backend_type, req.parameters)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Remote creation failed"))
    return res

@app.delete("/api/bclone/remotes/{name}")
async def delete_remote(name: str):
    """Delete a cloud remote."""
    res = await asyncio.to_thread(bclone.delete_remote, name)
    return res

@app.post("/api/bclone/crypt")
async def create_crypt_vault(req: CreateCryptVaultRequest):
    """Create an AES-256 client-side encrypted Crypt Vault."""
    res = await asyncio.to_thread(
        bclone.create_crypt_vault,
        req.vault_name,
        req.base_remote,
        req.base_path,
        req.password,
        req.salt,
        req.filename_encryption,
        req.directory_name_encryption
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Vault creation failed"))
    return res

@app.get("/api/bclone/files")
async def list_cloud_files(remote: str = Query(...), path: str = Query("")):
    """Browse files inside a cloud remote or decrypted Crypt Vault."""
    target = f"{remote}:{path}".rstrip(":")
    files = await asyncio.to_thread(bclone.list_files, target)
    return {"success": True, "target": target, "files": files}

@app.post("/api/bclone/test")
async def test_remote(req: TestRemoteRequest):
    """Test connectivity to cloud remote."""
    res = await asyncio.to_thread(bclone.test_remote_connection, req.remote_name)
    return res

@app.get("/api/bclone/config/raw")
async def get_raw_config():
    """Retrieve raw bclone.conf contents."""
    text = await asyncio.to_thread(bclone.get_raw_config_text)
    return {"success": True, "config": text}

@app.post("/api/bclone/config/raw")
async def save_raw_config(req: RawConfigRequest):
    """Update raw bclone.conf directly."""
    res = await asyncio.to_thread(bclone.set_raw_config_text, req.config_text)
    return res

# ----------------- Tor Anonymity Endpoints -----------------

@app.get("/api/tor/status")
async def get_tor_status(refresh: bool = False):
    """Inspect Tor SOCKS5 daemon status and verify public IP anonymity."""
    identity = await asyncio.to_thread(tor_engine.get_network_identity, refresh)
    return {"success": True, "identity": identity}

@app.post("/api/tor/newnym")
async def rotate_tor_identity():
    """Send SIGNAL NEWNYM to rotate Tor circuit and obtain a fresh exit IP."""
    res = await asyncio.to_thread(tor_engine.rotate_identity)
    return res

# ----------------- Local Storage Endpoints -----------------

@app.get("/api/downloads/local")
async def list_local_downloads():
    """List downloaded files in local downloads folder."""
    files = []
    if DOWNLOADS_DIR.exists():
        for p in DOWNLOADS_DIR.glob("*"):
            if p.is_file() and not p.name.endswith(".part") and not p.name.endswith(".ytdl"):
                files.append({
                    "name": p.name,
                    "size_bytes": p.stat().st_size,
                    "modified": p.stat().st_mtime,
                    "path": str(p)
                })
    files.sort(key=lambda x: x["modified"], reverse=True)
    return {"success": True, "files": files}

# ----------------- WebSockets & Static Assets -----------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

# Mount Web Dashboard
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

def main():
    import uvicorn
    host = APP_CONFIG["host"]
    port = APP_CONFIG["port"]
    print("==================================================================")
    print(f"      Z.Dip Sovereign Engine v{APP_CONFIG['version']}")
    print(f"      Listening on: http://{host}:{port}")
    print("==================================================================")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()

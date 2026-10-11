"""
Z.Dip Command-Line Interface (CLI)

Provides command-line control for video/media extraction,
cloud synchronization, Tor routing, and server management.
"""

import sys
import json
import argparse
from pathlib import Path
from zdip.config import APP_CONFIG
from zdip.protocols import extract, list_protocols, reinforce_protocol
from zdip.core.bclone_bridge import bclone
from zdip.core.tor_engine import tor_engine
from zdip.core.download_manager import download_manager

def cmd_extract(args):
    """Extract stream metadata from any URL or magnet URI."""
    opts = {
        "use_tor": args.tor,
        "proxy_url": tor_engine.get_proxy_url() if args.tor else None
    }
    print(f"\n[>] Extracting media via Z.Dip Protocol Engine: {args.url}")
    res = extract(args.url, opts)
    if not res.success:
        print(f"[!] Extraction failed: {res.error}")
        sys.exit(1)

    print("----------------------------------------------------------------")
    print(f"Title:     {res.title}")
    print(f"Protocol:  {res.protocol}")
    print(f"Type:      {res.media_type}")
    print(f"Uploader:  {res.uploader}")
    if res.is_onion:
        print(f"Tor Onion: Routed through .onion hidden network")
    if res.metadata.get("info_hash"):
        print(f"InfoHash:  {res.metadata['info_hash']}")
        print(f"Trackers:  {res.metadata.get('trackers_count')} active")

    if res.video_qualities:
        print("\nAvailable Streams:")
        for q in res.video_qualities:
            f_id = q.get("format_id", "")
            label = q.get("label", "")
            ext = q.get("ext", "")
            size = f"({q.get('filesize') // 1048576} MB)" if q.get("filesize") else ""
            print(f"  • [{f_id}] {label} .{ext} {size}")

    if res.audio_qualities:
        print("\nAvailable Audio:")
        for a in res.audio_qualities:
            f_id = a.get("format_id", "")
            label = a.get("label", "")
            ext = a.get("ext", "")
            print(f"  • [{f_id}] {label} .{ext}")
    print("----------------------------------------------------------------\n")

def cmd_download(args):
    """Download stream or file and optionally sync to cloud."""
    print(f"\n[>] Initializing download: {args.url}")
    job = download_manager.create_job(
        url=args.url,
        title=args.title or "Z.Dip_Download",
        format_id=args.format,
        is_audio_only=args.audio_only,
        storage_mode="sync_copy" if args.cloud else "local",
        dest_remote=args.cloud or "",
        dest_folder=args.dest_folder,
        delete_local_after_sync=args.delete_local,
        use_tor=args.tor,
        segments=args.segments
    )
    print(f"[✓] Task Queued: Job ID [{job['job_id']}]")
    print(f"    Mode: {job['storage_mode']} | Segments: {job['segments']} | Tor: {job['use_tor']}")

def cmd_serve(args):
    """Launch the Web Dashboard and REST API server."""
    from zdip.server import main as server_main
    if args.host:
        APP_CONFIG["host"] = args.host
    if args.port:
        APP_CONFIG["port"] = args.port
    server_main()

def cmd_protocols(args):
    """List or reinforce media protocols."""
    if args.reinforce:
        name, rule_str = args.reinforce
        try:
            k, v = rule_str.split("=", 1)
            rules = {k: v}
        except ValueError:
            rules = json.loads(rule_str)
        ok = reinforce_protocol(name, rules)
        print(f"Reinforce '{name}': {'Success' if ok else 'Failed'}")
    else:
        print("\nRegistered Z.Dip Media Protocols:")
        for p in list_protocols():
            print(f"  • [{p['priority']}] {p['name']} ({p['custom_rules_count']} custom rules)")
        print()

def cmd_tor(args):
    """Inspect or rotate Tor Onion network identity."""
    if args.rotate:
        print("[>] Sending SIGNAL NEWNYM to rotate Tor circuit...")
        res = tor_engine.rotate_identity()
        print(f"Result: {res.get('message', res)}")
    else:
        ident = tor_engine.get_network_identity(force_refresh=True)
        print("\nTor Network Identity:")
        print(f"  Clearnet IP:  {ident.get('clearnet_ip')}")
        print(f"  Tor SOCKS5:   {'Active' if ident.get('tor_running') else 'Offline'}")
        print(f"  Tor Exit IP:  {ident.get('tor_exit_ip') or 'N/A'}")
        print(f"  Anonymous:    {ident.get('is_anonymous')}\n")

def cmd_cloud(args):
    """List or test bclone cloud storage remotes."""
    remotes = bclone.list_remotes()
    print("\nConfigured Cloud Remotes:")
    if not remotes:
        print("  (No remotes configured yet. Use dashboard or bclone.conf)")
    for r in remotes:
        crypt = " [AES-256 Crypt Vault]" if r.get("is_crypt") else ""
        print(f"  • {r['name']} ({r['type']}){crypt}")
    print()

def main():
    parser = argparse.ArgumentParser(
        prog="zdip",
        description="Z.Dip • Media Extraction, BitTorrent & Multi-Cloud Privacy Engine"
    )
    sub = parser.add_subparsers(dest="command")

    # Extract
    p_ext = sub.add_parser("extract", help="Extract streams & formats from URL or Magnet")
    p_ext.add_argument("url", help="Media URL, video link, or magnet URI")
    p_ext.add_argument("--tor", action="store_true", help="Route extraction through Tor")

    # Download
    p_dl = sub.add_parser("download", help="Download media or stream")
    p_dl.add_argument("url", help="Media URL, video link, or magnet URI")
    p_dl.add_argument("--title", default=None, help="Custom output title")
    p_dl.add_argument("--format", default="best", help="Format selector")
    p_dl.add_argument("--audio-only", action="store_true", help="Extract audio only")
    p_dl.add_argument("--cloud", default=None, help="Target bclone remote (e.g. terabox, gdrive, vault)")
    p_dl.add_argument("--dest-folder", default="ZytorMedia", help="Destination folder on cloud remote")
    p_dl.add_argument("--delete-local", action="store_true", help="Delete local file after cloud sync")
    p_dl.add_argument("--tor", action="store_true", help="Route download through Tor proxy")
    p_dl.add_argument("--segments", type=int, default=16, help="Parallel TurboBolt segments (1-64)")

    # Serve
    p_srv = sub.add_parser("serve", help="Launch Web Dashboard & REST API")
    p_srv.add_argument("--host", default=None, help="Host address")
    p_srv.add_argument("--port", type=int, default=None, help="Port number")

    # Protocols
    p_proto = sub.add_parser("protocols", help="List and reinforce protocol extractors")
    p_proto.add_argument("--reinforce", nargs=2, metavar=("PROTOCOL", "RULE"), help="Reinforce protocol")

    # Tor
    p_tor = sub.add_parser("tor", help="Inspect or rotate Tor circuit")
    p_tor.add_argument("--rotate", action="store_true", help="Rotate Tor identity (NEWNYM)")

    # Cloud
    sub.add_parser("cloud", help="List configured cloud storage remotes")

    args = parser.parse_args()
    if args.command == "extract":
        cmd_extract(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "protocols":
        cmd_protocols(args)
    elif args.command == "tor":
        cmd_tor(args)
    elif args.command == "cloud":
        cmd_cloud(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

import os
import sys
import json
import subprocess
import threading
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
try:
    from zdip.config import BCLONE_EXE, BCLONE_CONF
except ImportError:
    from .config import BCLONE_EXE, BCLONE_CONF


logger = logging.getLogger("bclone_bridge")
logging.basicConfig(level=logging.INFO)

SYSTEM_RCLONE_CONF = Path(os.environ.get("APPDATA", "")) / "rclone" / "rclone.conf"

class BcloneBridge:
    def __init__(self, exe_path: Optional[Path] = None, conf_path: Optional[Path] = None):
        self.exe = str(exe_path or BCLONE_EXE)
        self.conf = str(conf_path or BCLONE_CONF)
        
        # Initialize config file if missing, auto-import system rclone.conf if present
        if not os.path.exists(self.conf):
            if SYSTEM_RCLONE_CONF.exists() and SYSTEM_RCLONE_CONF.stat().st_size > 0:
                try:
                    with open(SYSTEM_RCLONE_CONF, "r", encoding="utf-8", errors="ignore") as sf:
                        content = sf.read()
                    with open(self.conf, "w", encoding="utf-8") as df:
                        df.write(content)
                    logger.info("Imported existing system rclone.conf into Zytor bclone.conf")
                except Exception as e:
                    logger.warning(f"Could not import system rclone.conf: {e}")
            else:
                with open(self.conf, "w", encoding="utf-8") as f:
                    f.write("# Zytor Sovereign bclone configuration\n")

    def _run_cmd(self, args: List[str], timeout: int = 30, input_data: Optional[str] = None) -> Dict[str, Any]:
        cmd = [self.exe, "--config", self.conf] + args
        try:
            p = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return {
                "success": p.returncode == 0,
                "returncode": p.returncode,
                "stdout": p.stdout or "",
                "stderr": p.stderr or "",
                "cmd": cmd
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": "Command timed out (make sure --non-interactive is used)", "cmd": cmd}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e), "cmd": cmd}

    def list_remotes(self) -> List[Dict[str, Any]]:
        """List all configured remotes with their backend types and crypt status."""
        res = self._run_cmd(["config", "dump", "--non-interactive"])
        if not res["success"]:
            # Fallback: try reading sections from bclone.conf directly
            return self._parse_conf_sections()

        try:
            data = json.loads(res["stdout"]) if res["stdout"].strip() else {}
            remotes = []
            for name, conf in data.items():
                b_type = conf.get("type", "unknown")
                is_crypt = b_type == "crypt"
                remotes.append({
                    "name": name,
                    "type": b_type,
                    "is_crypt": is_crypt,
                    "remote": conf.get("remote", "") if is_crypt else None,
                    "filename_encryption": conf.get("filename_encryption", "") if is_crypt else None,
                    "directory_name_encryption": conf.get("directory_name_encryption", "") if is_crypt else None,
                    "description": f"{name} ({b_type})"
                })
            return remotes
        except Exception as e:
            logger.error(f"Failed to parse config dump: {e}")
            return self._parse_conf_sections()

    def _parse_conf_sections(self) -> List[Dict[str, Any]]:
        """Direct INI parser fallback."""
        if not os.path.exists(self.conf):
            return []
        remotes = []
        curr = None
        curr_type = "unknown"
        is_crypt = False
        target_remote = ""
        
        with open(self.conf, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    if curr:
                        remotes.append({
                            "name": curr,
                            "type": curr_type,
                            "is_crypt": is_crypt,
                            "remote": target_remote if is_crypt else None
                        })
                    curr = line[1:-1]
                    curr_type = "unknown"
                    is_crypt = False
                    target_remote = ""
                elif "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k == "type":
                        curr_type = v
                        is_crypt = (v == "crypt")
                    elif k == "remote":
                        target_remote = v
            if curr:
                remotes.append({
                    "name": curr,
                    "type": curr_type,
                    "is_crypt": is_crypt,
                    "remote": target_remote if is_crypt else None
                })
        return remotes

    def get_raw_config(self) -> str:
        """Return the contents of bclone.conf."""
        if os.path.exists(self.conf):
            with open(self.conf, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""

    def save_raw_config(self, text: str) -> Dict[str, Any]:
        """Save raw text to bclone.conf."""
        try:
            with open(self.conf, "w", encoding="utf-8") as f:
                f.write(text)
            return {"success": True, "message": "Configuration saved"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def import_system_config(self) -> Dict[str, Any]:
        """Import remotes from Windows/Linux default rclone.conf."""
        candidates = [
            SYSTEM_RCLONE_CONF,
            Path.home() / ".config" / "rclone" / "rclone.conf"
        ]
        imported = False
        for c in candidates:
            if c.exists() and c.stat().st_size > 0:
                try:
                    with open(c, "r", encoding="utf-8", errors="ignore") as sf:
                        sys_content = sf.read()
                    with open(self.conf, "a", encoding="utf-8") as df:
                        df.write("\n\n# --- Imported from " + str(c) + " ---\n" + sys_content)
                    imported = True
                    break
                except Exception:
                    pass
        if imported:
            return {"success": True, "message": "Imported system rclone remotes!"}
        return {"success": False, "message": "No system rclone.conf found with active remotes."}

    def create_remote(self, name: str, backend_type: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a new remote in bclone.conf non-interactively.
        Properly obscures sensitive password fields.
        """
        clean_params = {}
        for k, v in params.items():
            if v is not None and str(v).strip() != "":
                # Obscure password fields for backends like mega, webdav, sftp, etc.
                if k in ("pass", "password") and backend_type in ("mega", "webdav", "sftp", "smb", "ftp"):
                    clean_params[k] = self._obscure_string(str(v).strip())
                else:
                    clean_params[k] = str(v).strip()

        args = ["config", "create", name, backend_type, "--non-interactive"]
        for k, v in clean_params.items():
            args.append(f"{k}={v}")

        res = self._run_cmd(args, timeout=20)
        
        # If config create failed or hung, fallback to direct INI writing
        if not res["success"]:
            logger.info(f"config create returned error, applying direct INI write fallback for {name}")
            return self._write_remote_ini(name, backend_type, clean_params)
        
        return res

    def _write_remote_ini(self, name: str, backend_type: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Directly writes remote section to bclone.conf."""
        try:
            lines = [f"\n[{name}]", f"type = {backend_type}"]
            for k, v in params.items():
                lines.append(f"{k} = {v}")
            lines.append("\n")

            with open(self.conf, "a", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return {"success": True, "message": f"Remote {name} written successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_remote(self, name: str) -> Dict[str, Any]:
        """Delete an existing remote."""
        res = self._run_cmd(["config", "delete", name])
        if not res["success"]:
            # Direct INI delete fallback
            try:
                content = self.get_raw_config()
                lines = content.splitlines()
                new_lines = []
                skipping = False
                for l in lines:
                    if l.strip() == f"[{name}]":
                        skipping = True
                        continue
                    elif skipping and l.strip().startswith("[") and l.strip().endswith("]"):
                        skipping = False
                    if not skipping:
                        new_lines.append(l)
                self.save_raw_config("\n".join(new_lines))
                return {"success": True, "message": f"Deleted {name}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return res

    def create_crypt_vault(
        self,
        vault_name: str,
        base_remote: str,
        base_path: str = "EncryptedVault",
        password: str = "",
        salt: str = "",
        filename_encryption: str = "standard",
        directory_name_encryption: bool = True
    ) -> Dict[str, Any]:
        """
        Creates a zero-knowledge encrypted bclone remote wrapping an existing remote.
        Example: vault_name="my_secret_drive", base_remote="gdrive", base_path="Vault"
        """
        target = f"{base_remote}:{base_path.strip('/')}"
        
        pwd_obscure = self._obscure_string(password) if password else ""
        salt_obscure = self._obscure_string(salt) if salt else ""

        params = {
            "remote": target,
            "filename_encryption": filename_encryption,
            "directory_name_encryption": "true" if directory_name_encryption else "false",
        }
        if pwd_obscure:
            params["password"] = pwd_obscure
        if salt_obscure:
            params["password2"] = salt_obscure

        return self.create_remote(vault_name, "crypt", params)

    def _obscure_string(self, raw: str) -> str:
        """Obscures password using bclone obscure."""
        res = self._run_cmd(["obscure", raw])
        if res["success"] and res["stdout"].strip():
            return res["stdout"].strip()
        return raw

    def test_connection(self, remote_name: str) -> Dict[str, Any]:
        """Verify remote connectivity and credentials using lsf."""
        target = f"{remote_name}:"
        res = self._run_cmd(["lsf", target, "--max-depth", "1"], timeout=15)
        return {
            "success": res["success"],
            "message": "Connection verified successfully!" if res["success"] else (res["stderr"].strip() or "Connection test failed"),
            "remote": remote_name
        }

    def list_files(self, remote_path: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """List files and directories on remote path using lsjson."""
        target = remote_path if ":" in remote_path else f"{remote_path}:"
        res = self._run_cmd(["lsjson", target, "--max-depth", str(max_depth)], timeout=25)
        if not res["success"]:
            return []
        try:
            return json.loads(res["stdout"])
        except Exception:
            return []

    def copy_file(
        self,
        local_filepath: str,
        dest_remote: str,
        dest_folder: str = "",
        move: bool = False,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Copy or move local file to remote storage."""
        target = f"{dest_remote}:{dest_folder.strip('/')}"
        action = "move" if move else "copy"
        
        args = [
            action,
            local_filepath,
            target,
            "--stats", "1s",
            "--stats-one-line",
            "--use-json-log",
            "-v"
        ]
        
        cmd = [self.exe, "--config", self.conf] + args
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            def monitor_stderr():
                for line in proc.stderr:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        log_obj = json.loads(line)
                        if on_progress and "stats" in log_obj:
                            on_progress(log_obj["stats"])
                    except Exception:
                        pass

            t = threading.Thread(target=monitor_stderr, daemon=True)
            t.start()
            proc.wait()
            t.join(timeout=2)

            return {
                "success": proc.returncode == 0,
                "returncode": proc.returncode,
                "remote_path": f"{target}/{os.path.basename(local_filepath)}"
            }
        except Exception as e:
            return {"success": False, "returncode": -1, "error": str(e)}

    def get_rcat_process(self, dest_remote: str, dest_folder: str, filename: str) -> subprocess.Popen:
        """Returns a Popen process for zero-disk direct rcat streaming into cloud storage."""
        clean_folder = dest_folder.strip('/')
        target = f"{dest_remote}:{clean_folder}/{filename}" if clean_folder else f"{dest_remote}:{filename}"
        cmd = [self.exe, "--config", self.conf, "rcat", target, "--stats", "1s", "-v"]
        
        return subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def get_supported_backends(self) -> List[Dict[str, Any]]:
        """Return prominent backends supported by bclone with detailed parameter templates."""
        return [
            {
                "id": "terabox",
                "name": "Terabox (Bclone Enhanced)",
                "category": "High Capacity Cloud",
                "desc": "Terabox cloud storage with native bclone driver.",
                "fields": [
                    {"key": "cookie", "label": "Terabox Cookie (ndus)", "type": "text", "placeholder": "ndus=...", "required": True}
                ]
            },
            {
                "id": "alist",
                "name": "AList (Bclone Enhanced - 30+ Clouds)",
                "category": "Cloud Aggregator",
                "desc": "Universal gateway for Baidu, Quark, 115, PikPak, Alist-backed drivers.",
                "fields": [
                    {"key": "url", "label": "AList Server URL", "type": "text", "placeholder": "https://alist.example.com", "required": True},
                    {"key": "password", "label": "Password / Token", "type": "password", "placeholder": "AList admin token or password", "required": True}
                ]
            },
            {
                "id": "teldrive",
                "name": "Tel Drive (Bclone Enhanced)",
                "category": "Telegram Storage",
                "desc": "Unlimited cloud storage leveraging Telegram API channels.",
                "fields": [
                    {"key": "api_host", "label": "TelDrive API Host", "type": "text", "placeholder": "https://teldrive.example.com", "required": True},
                    {"key": "jwt_token", "label": "JWT Access Token", "type": "password", "placeholder": "eyJhbGciOi...", "required": True}
                ]
            },
            {
                "id": "gotohp",
                "name": "Google Photos (Bclone Enhanced Unofficial)",
                "category": "Media Cloud",
                "desc": "Unofficial direct media backup to Google Photos.",
                "fields": [
                    {"key": "token", "label": "Google Photos Auth Token", "type": "password", "placeholder": "Auth token JSON", "required": True}
                ]
            },
            {
                "id": "mega",
                "name": "Mega.nz",
                "category": "Direct Cloud",
                "desc": "End-to-end encrypted Mega cloud storage.",
                "fields": [
                    {"key": "user", "label": "Mega Email / Username", "type": "text", "placeholder": "user@example.com", "required": True},
                    {"key": "pass", "label": "Mega Password", "type": "password", "placeholder": "Mega account password", "required": True}
                ]
            },
            {
                "id": "webdav",
                "name": "WebDAV (Nextcloud / ownCloud / Seedbox)",
                "category": "Self-Hosted & Seedbox",
                "desc": "Standard WebDAV endpoint for personal clouds and servers.",
                "fields": [
                    {"key": "url", "label": "WebDAV Server URL", "type": "text", "placeholder": "https://cloud.example.com/remote.php/dav/files/user/", "required": True},
                    {"key": "vendor", "label": "Vendor", "type": "text", "placeholder": "nextcloud, owncloud, other", "required": False},
                    {"key": "user", "label": "Username", "type": "text", "placeholder": "webdav_user", "required": True},
                    {"key": "pass", "label": "Password / App Token", "type": "password", "placeholder": "password", "required": True}
                ]
            },
            {
                "id": "s3",
                "name": "Amazon S3 / Cloudflare R2 / MinIO / Wasabi",
                "category": "Object Storage",
                "desc": "High performance S3-compatible bucket storage.",
                "fields": [
                    {"key": "provider", "label": "Provider", "type": "text", "placeholder": "AWS, Cloudflare, Minio, Wasabi", "required": True},
                    {"key": "access_key_id", "label": "Access Key ID", "type": "text", "placeholder": "Access Key", "required": True},
                    {"key": "secret_access_key", "label": "Secret Access Key", "type": "password", "placeholder": "Secret Key", "required": True},
                    {"key": "endpoint", "label": "Endpoint URL (for R2/MinIO)", "type": "text", "placeholder": "e.g. https://<account>.r2.cloudflarestorage.com", "required": False},
                    {"key": "region", "label": "Region", "type": "text", "placeholder": "auto or us-east-1", "required": False}
                ]
            },
            {
                "id": "drive",
                "name": "Google Drive",
                "category": "Standard Cloud",
                "desc": "Google Drive storage (paste OAuth2 token or service account credentials).",
                "fields": [
                    {"key": "token", "label": "OAuth2 Token JSON (or use rclone config)", "type": "text", "placeholder": "{\"access_token\":\"...\"}", "required": False},
                    {"key": "service_account_file", "label": "Service Account JSON Path (optional)", "type": "text", "placeholder": "C:\\path\\to\\credentials.json", "required": False}
                ]
            },
            {
                "id": "onedrive",
                "name": "Microsoft OneDrive",
                "category": "Standard Cloud",
                "desc": "Microsoft OneDrive personal or business storage.",
                "fields": [
                    {"key": "token", "label": "OAuth2 Token JSON", "type": "text", "placeholder": "{\"access_token\":\"...\"}", "required": False}
                ]
            },
            {
                "id": "dropbox",
                "name": "Dropbox",
                "category": "Standard Cloud",
                "desc": "Dropbox cloud storage.",
                "fields": [
                    {"key": "token", "label": "OAuth2 Token JSON", "type": "text", "placeholder": "{\"access_token\":\"...\"}", "required": False}
                ]
            },
            {
                "id": "local",
                "name": "External Drive / Local Custom Directory",
                "category": "Local / NAS",
                "desc": "External hard drive, USB storage, or custom local folder.",
                "fields": [
                    {"key": "path", "label": "Directory Path", "type": "text", "placeholder": "D:\\MediaBackups or \\\\NAS\\Share", "required": False}
                ]
            },
            {
                "id": "crypt",
                "name": "AES-256 Encrypted Crypt Vault",
                "category": "Zero-Knowledge Security",
                "desc": "Client-side encrypted overlay remote on top of ANY storage remote.",
                "fields": []
            }
        ]

bclone = BcloneBridge()

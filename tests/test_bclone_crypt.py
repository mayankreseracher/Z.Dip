"""
Unit tests for Z.Dip bclone cloud storage & AES-256 Crypt Vault
"""

import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from zdip.core.bclone_bridge import bclone

def test_bclone_backends():
    backends = bclone.get_supported_backends()
    assert len(backends) > 0
    backend_ids = [b["id"] for b in backends]
    assert "drive" in backend_ids
    assert "terabox" in backend_ids

def test_crypt_vault_lifecycle():
    # Setup test local folder
    test_dir = BASE_DIR / "tests" / "temp_cloud"
    test_dir.mkdir(parents=True, exist_ok=True)

    remote_name = "test_zdip_local"
    vault_name = "test_zdip_crypt"

    # Create local remote
    bclone.create_remote(remote_name, "local", {})
    
    # Create Crypt Vault
    res = bclone.create_crypt_vault(
        vault_name=vault_name,
        base_remote=remote_name,
        base_path=str(test_dir).replace("\\", "/"),
        password="zdip_test_encryption_key_2026",
        salt="zdip_salt_test",
        filename_encryption="standard",
        directory_name_encryption=True
    )
    assert res["success"] is True

    # Check remotes
    remotes = bclone.list_remotes()
    remote_names = [r["name"] for r in remotes]
    assert vault_name in remote_names

    # Clean up
    bclone.delete_remote(vault_name)
    bclone.delete_remote(remote_name)
    shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    test_bclone_backends()
    test_crypt_vault_lifecycle()
    print("bclone & Crypt Vault tests passed successfully!")

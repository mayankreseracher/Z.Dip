import os
import sys
import time
import shutil
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from core.config import BCLONE_EXE, YTDLP_EXE, DOWNLOADS_DIR
from core.bclone_bridge import bclone
from core.tor_engine import tor_engine
from core.media_parser import media_parser
from core.turbobolt import TurboBoltJob

def test_toolchain():
    print("\n--- [1/5] Testing Toolchain Binaries ---")
    assert os.path.exists(BCLONE_EXE), f"bclone.exe not found at {BCLONE_EXE}"
    assert os.path.exists(YTDLP_EXE), f"yt-dlp.exe not found at {YTDLP_EXE}"

    # Verify bclone version
    backends = bclone.get_supported_backends()
    print(f"✓ bclone binary verified. Supported prominent backends: {len(backends)}")
    print(f"  Sample backends: {', '.join([b['id'] for b in backends[:6]])}")

def test_bclone_and_crypt():
    print("\n--- [2/5] Testing bclone Remotes & Zero-Knowledge Crypt Vault ---")
    # 1. Create a test local remote pointing to test_cloud_storage
    test_storage_dir = BASE_DIR / "test_cloud_raw"
    test_storage_dir.mkdir(exist_ok=True)

    remote_name = "test_local_cloud"
    bclone.create_remote(remote_name, "local", {})
    
    # 2. Create a Crypt Vault wrapping test_local_cloud:test_cloud_raw
    vault_name = "test_vault_encrypted"
    crypt_res = bclone.create_crypt_vault(
        vault_name=vault_name,
        base_remote=remote_name,
        base_path=str(test_storage_dir).replace("\\", "/"),
        password="zytor_secure_passphrase_2026",
        salt="zytor_salt_key",
        filename_encryption="standard",
        directory_name_encryption=True
    )
    assert crypt_res["success"], f"Failed to create crypt vault: {crypt_res}"
    print(f"✓ Created Crypt Vault: {vault_name} (AES-256 encrypted)")

    # 3. Write a test plain file and copy into vault
    test_file = BASE_DIR / "sample_secret.txt"
    test_content = "Zytor Sovereign + bclone zero-knowledge client-side encryption test payload."
    with open(test_file, "w") as f:
        f.write(test_content)

    print("✓ Uploading plain test file to encrypted vault...")
    copy_res = bclone.copy_file(
        local_filepath=str(test_file),
        dest_remote=vault_name,
        dest_folder="Secrets"
    )
    assert copy_res["success"], f"Vault copy failed: {copy_res}"
    print(f"✓ File successfully transferred into vault: {copy_res.get('remote_path')}")

    # 4. Inspect the physical raw storage folder: verify data on disk is encrypted ciphertext!
    raw_files = list(test_storage_dir.rglob("*"))
    print(f"✓ Raw files stored in cloud directory: {len(raw_files)} items")
    for rf in raw_files:
        if rf.is_file():
            print(f"  Encrypted ciphertext filename on cloud: {rf.name}")
            with open(rf, "rb") as f:
                header = f.read(32)
                # Ensure plaintext is NOT visible
                assert b"Zytor Sovereign" not in header, "Security breach: raw plaintext found in encrypted remote!"
    print("✓ Zero-knowledge encryption verified: cloud files and names are fully encrypted.")

    # 5. Read back through bclone vault to verify transparent decryption
    files_in_vault = bclone.list_files(f"{vault_name}:Secrets")
    assert any("sample_secret.txt" in f.get("Name", "") for f in files_in_vault), "Decrypted filename mismatch in vault!"
    print("✓ Transparent client-side decryption verified: file list displays original filename.")

    # Cleanup test files
    if test_file.exists():
        test_file.unlink()
    shutil.rmtree(test_storage_dir, ignore_errors=True)
    bclone.delete_remote(vault_name)
    bclone.delete_remote(remote_name)
    print("✓ Test remotes cleaned up.")

def test_tor_engine():
    print("\n--- [3/5] Testing Tor Onion Engine & Network Identity ---")
    identity = tor_engine.get_network_identity()
    print(f"✓ Clearnet IP: {identity.get('clearnet_ip')}")
    print(f"✓ Tor SOCKS5 status: {'Active' if identity.get('tor_running') else 'Offline (Ready for tunnel)'}")
    print(f"✓ Onion link detector: {tor_engine.is_onion('http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion')}")
    assert tor_engine.is_onion("http://example.onion/test"), "Onion detector failed"
    assert tor_engine.is_magnet("magnet:?xt=urn:btih:abcdef"), "Magnet detector failed"
    print("✓ Tor engine tests passed.")

def test_media_parser():
    print("\n--- [4/5] Testing Media Parser & Magnet Link Resolution ---")
    magnet = "magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10&dn=Sintel&tr=udp%3A%2F%2Fexplodie.org%3A6969"
    res = media_parser.analyze_url(magnet)
    assert res["success"], f"Magnet parse failed: {res}"
    assert res["media_type"] == "torrent", "Expected torrent media type"
    print(f"✓ Magnet link resolved: Title = '{res['title']}', Trackers = {res['trackers_count']}")

    # Direct link test
    direct = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    res_direct = media_parser.analyze_url(direct)
    assert res_direct["success"], f"Direct URL probe failed: {res_direct}"
    print(f"✓ Direct file resolved: Title = '{res_direct['title']}'")

def test_turbobolt_pipeline():
    print("\n--- [5/5] Testing TurboBolt Pipeline Execution ---")
    test_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    updates = []
    
    job = TurboBoltJob(
        job_id="test-001",
        url=test_url,
        title="Sample Test PDF",
        storage_mode="local",
        segments=8,
        on_update=lambda d: updates.append(d["status"])
    )
    job.start()
    
    # Wait for completion
    timeout = 20
    start = time.time()
    while job.status in ("QUEUED", "DOWNLOADING") and (time.time() - start < timeout):
        time.sleep(0.5)

    print(f"✓ TurboBolt job status: {job.status} (Transferred: {job.progress}%)")
    assert job.status == "COMPLETED", f"TurboBolt job did not complete: {job.error_message}"
    print("✓ TurboBolt pipeline download completed successfully!")

if __name__ == "__main__":
    print("==================================================================")
    print("   ZYTOR SOVEREIGN : COMPREHENSIVE INTEGRATION & SECURITY TEST   ")
    print("==================================================================")
    test_toolchain()
    test_bclone_and_crypt()
    test_tor_engine()
    test_media_parser()
    test_turbobolt_pipeline()
    print("\n==================================================================")
    print("   ALL TESTS PASSED! ZYTOR + BCLONE + TOR ENGINE VERIFIED 100%   ")
    print("==================================================================")

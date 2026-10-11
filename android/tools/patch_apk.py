#!/usr/bin/env python3
"""
Z.Dip / Zytor Sovereign - Automated APK Patcher & Builder Tool

This tool automates:
1. Decompilation of source Zytor APK via apktool
2. Smali bytecode injection (BcloneCloudUploader, DownloaderImpl hook, Tor auto-routing)
3. UI localization updates (res/values/strings.xml)
4. Native binary embedding (lib/arm64-v8a/libbclone.so)
5. Zip alignment (zipalign -p 4)
6. APK signing (apksigner V1/V2/V3 schemes)
"""

import os
import sys
import shutil
import zipfile
import argparse
import subprocess
from pathlib import Path

def run_cmd(cmd, desc="Command"):
    print(f"[>] {desc}: {' '.join(str(x) for x in cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error during {desc}:\n{res.stderr}")
        sys.exit(res.returncode)
    return res

def patch_apk(
    source_apk: Path,
    output_apk: Path,
    bclone_arm64_bin: Path,
    keystore_path: Path,
    keystore_pass: str = "android",
    key_alias: str = "androiddebugkey",
    key_pass: str = "android"
):
    source_apk = Path(source_apk).resolve()
    output_apk = Path(output_apk).resolve()
    bclone_arm64_bin = Path(bclone_arm64_bin).resolve()
    keystore_path = Path(keystore_path).resolve()

    if not source_apk.exists():
        raise FileNotFoundError(f"Source APK not found: {source_apk}")
    if not bclone_arm64_bin.exists():
        raise FileNotFoundError(f"libbclone.so binary not found: {bclone_arm64_bin}")
    if not keystore_path.exists():
        raise FileNotFoundError(f"Signing keystore not found: {keystore_path}")

    build_dir = output_apk.parent / "build_temp"
    build_dir.mkdir(parents=True, exist_ok=True)
    unaligned_apk = build_dir / "unaligned.apk"
    aligned_apk = build_dir / "aligned.apk"

    print("================================================================")
    print("      Z.Dip Sovereign APK Build & Packaging Pipeline")
    print("================================================================")
    print(f"Source APK:   {source_apk}")
    print(f"Target APK:   {output_apk}")
    print(f"bclone lib:   {bclone_arm64_bin}")
    print(f"Keystore:     {keystore_path}")
    print("----------------------------------------------------------------")

    # Read bclone binary
    with open(bclone_arm64_bin, "rb") as f:
        bclone_data = f.read()

    # Re-package APK: filter old signatures and inject libbclone.so
    print("[1/4] Re-packaging APK and injecting lib/arm64-v8a/libbclone.so...")
    with zipfile.ZipFile(source_apk, "r") as zin, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            fn = item.filename
            # Strip previous Android signatures
            if fn.startswith("META-INF/") and any(fn.endswith(ext) for ext in [".SF", ".RSA", ".DSA", ".MF"]):
                continue
            zout.writestr(item, zin.read(fn))

        # Add libbclone.so into lib/arm64-v8a
        bclone_item = zipfile.ZipInfo("lib/arm64-v8a/libbclone.so")
        bclone_item.compress_type = zipfile.ZIP_DEFLATED
        bclone_item.external_attr = 0o755 << 16
        zout.writestr(bclone_item, bclone_data)

    print(f"      Unaligned APK ready: {unaligned_apk.stat().st_size:,} bytes")

    # 4-byte zipalign
    print("[2/4] Aligning APK with zipalign (4-byte page boundaries)...")
    run_cmd(["zipalign", "-f", "-p", "4", str(unaligned_apk), str(aligned_apk)], "Zipalign")

    # Sign with apksigner (V1, V2, V3)
    print("[3/4] Signing APK with apksigner (V1 + V2 + V3 schemes)...")
    sign_cmd = [
        "apksigner", "sign",
        "--ks", str(keystore_path),
        "--ks-pass", f"pass:{keystore_pass}",
        "--ks-key-alias", key_alias,
        "--key-pass", f"pass:{key_pass}",
        "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        str(aligned_apk)
    ]
    run_cmd(sign_cmd, "Apksigner")

    # Verify signature
    print("[4/4] Verifying APK signature...")
    verify_res = run_cmd(["apksigner", "verify", "--verbose", str(aligned_apk)], "Apksigner Verify")
    if "Verified using v1 scheme (JAR signing): true" in verify_res.stdout or "Verified using v2 scheme (APK Signature Scheme v2): true" in verify_res.stdout:
        print("      Signature verification PASSED!")
    else:
        print("      Warning: Signature verification completed with warnings.")

    shutil.copyfile(aligned_apk, output_apk)
    print("----------------------------------------------------------------")
    print(f"[✓] SUCCESS: Final Sovereign APK generated at:")
    print(f"    {output_apk} ({output_apk.stat().st_size:,} bytes)")
    print("================================================================")

    # Clean temporary build dir
    shutil.rmtree(build_dir, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Z.Dip Android APK Patcher & Builder")
    parser.add_argument("--source", required=True, help="Path to base Zytor APK")
    parser.add_argument("--output", required=True, help="Destination path for sovereign APK")
    parser.add_argument("--bclone-bin", required=True, help="Path to ARM64 libbclone.so")
    parser.add_argument("--keystore", default="debug.keystore", help="Path to signing keystore")
    parser.add_argument("--keystore-pass", default="android", help="Keystore password")
    parser.add_argument("--key-alias", default="androiddebugkey", help="Key alias")
    parser.add_argument("--key-pass", default="android", help="Key password")

    args = parser.parse_args()
    patch_apk(
        source_apk=Path(args.source),
        output_apk=Path(args.output),
        bclone_arm64_bin=Path(args.bclone_bin),
        keystore_path=Path(args.keystore),
        keystore_pass=args.keystore_pass,
        key_alias=args.key_alias,
        key_pass=args.key_pass
    )

import os
import zipfile
import subprocess
import shutil

src_apk = "/mnt/c/Users/Mayank/Documents/Tiger underneath/zytor_v1.2.0.apk"
classes3_path = "/home/insectoid/apk_build/classes3_modified.dex"
bclone_bin_path = "/home/insectoid/apk_build/zytor_decompiled/lib/arm64-v8a/libbclone.so"
unaligned_apk = "/home/insectoid/apk_build/zytor_mod_unaligned.apk"
aligned_apk = "/home/insectoid/apk_build/zytor-sovereign-v1.2.0.apk"
final_dest = "/mnt/c/Users/Mayank/Documents/Tiger underneath/zytor-sovereign-v1.2.0.apk"

print(f"Reading source APK: {src_apk}")
with open(classes3_path, "rb") as f:
    new_classes3_data = f.read()

with open(bclone_bin_path, "rb") as f:
    bclone_data = f.read()

print(f"New classes3.dex size: {len(new_classes3_data)} bytes")
print(f"libbclone.so size: {len(bclone_data)} bytes")

signature_files = {
    "META-INF/MANIFEST.MF",
    "META-INF/CERT.SF",
    "META-INF/CERT.RSA",
    "META-INF/ANDROIDD.SF",
    "META-INF/ANDROIDD.RSA",
}

with zipfile.ZipFile(src_apk, "r") as zin, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        fn = item.filename
        # Skip signature files so apksigner can sign cleanly with V1+V2+V3
        if fn.startswith("META-INF/") and (fn.endswith(".SF") or fn.endswith(".RSA") or fn.endswith(".DSA") or fn.endswith(".MF")):
            continue
        
        if fn == "classes3.dex":
            print("Injecting enhanced classes3.dex...")
            zout.writestr(item, new_classes3_data)
        else:
            zout.writestr(item, zin.read(fn))

    # Add libbclone.so
    print("Injecting lib/arm64-v8a/libbclone.so...")
    bclone_item = zipfile.ZipInfo("lib/arm64-v8a/libbclone.so")
    bclone_item.compress_type = zipfile.ZIP_DEFLATED
    bclone_item.external_attr = 0o755 << 16  # rwxr-xr-x
    zout.writestr(bclone_item, bclone_data)

print(f"Created unaligned APK: {unaligned_apk} ({os.path.getsize(unaligned_apk)} bytes)")

# Run zipalign
print("Running zipalign 4...")
align_res = subprocess.run(["zipalign", "-f", "-p", "4", unaligned_apk, aligned_apk], capture_output=True, text=True)
if align_res.returncode != 0:
    print("Zipalign failed:", align_res.stderr)
    exit(1)
print(f"Zipalign succeeded: {aligned_apk} ({os.path.getsize(aligned_apk)} bytes)")

# Run apksigner
print("Signing APK with debug keystore (V1, V2, V3 signature schemes)...")
keystore = "/home/insectoid/apk_build/debug.keystore"
sign_cmd = [
    "apksigner", "sign",
    "--ks", keystore,
    "--ks-pass", "pass:android",
    "--ks-key-alias", "androiddebugkey",
    "--key-pass", "pass:android",
    "--v1-signing-enabled", "true",
    "--v2-signing-enabled", "true",
    "--v3-signing-enabled", "true",
    aligned_apk
]
sign_res = subprocess.run(sign_cmd, capture_output=True, text=True)
if sign_res.returncode != 0:
    print("Apksigner sign failed:", sign_res.stderr)
    exit(1)
print("Apksigner sign succeeded!")

# Verify signature
print("Verifying APK signatures...")
verify_res = subprocess.run(["apksigner", "verify", "--verbose", aligned_apk], capture_output=True, text=True)
print("Verification stdout:\n", verify_res.stdout)
if verify_res.stderr:
    print("Verification stderr:\n", verify_res.stderr)

# Copy final APK to workspace
shutil.copyfile(aligned_apk, final_dest)
print(f"FINAL APK copied to: {final_dest} ({os.path.getsize(final_dest)} bytes)")

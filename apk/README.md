# 📲 Zytor Sovereign Edition - Android APK Release

This directory contains the pre-compiled, signed, and aligned Android APK package along with the bytecode smali patches used to build it.

---

## 📦 Delivered Artifacts

- **`zytor-sovereign-v1.2.0.apk`** (85.5 MB)
  - Pre-compiled Android application package.
  - Aligned to 4-byte boundaries (`zipalign 4`).
  - Signed with Android V2 and V3 signature schemes.
  - Compatible with Android 7.0 (API 24) through Android 15+.

---

## 🛠️ Included Patches & Scripts (`patches/`)

1. **`BcloneCloudUploader.smali`**
   - Dalvik bytecode class for managing background cloud auto-transfers and creating default `bclone.conf` configurations.
2. **`patch_downloader_impl.py`**
   - Injects the `BcloneCloudUploader.uploadIfEnabled` trigger into `DownloaderImpl$download$1` at download completion.
3. **`patch_pref_model_tor.py`**
   - Patches `DownloadPreferences` to automatically activate SOCKS5 Tor proxying (`socks5://127.0.0.1:9050`) whenever `tor_enabled` is switched ON.
4. **`build_modified_apk.py`**
   - Automates unaligned APK packaging, `libbclone.so` ARM64 binary injection, `zipalign` alignment, and `apksigner` signing.

---

## 📲 How to Install

Via **ADB**:
```bash
adb install -r zytor-sovereign-v1.2.0.apk
```
Or transfer `zytor-sovereign-v1.2.0.apk` directly to your phone and install via any Android File Manager.

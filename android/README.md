# 📱 Z.Dip Mobile • Android Sovereign Edition

The **Android Sovereign Edition** integrates direct-to-cloud synchronization and onion anonymity directly into the native Android application package (`.apk`).

---

## 🚀 Key Mobile Features

- **Embedded `libbclone.so` ARM64 Engine:**
  Native compilation of bclone bundled directly inside the APK's `lib/arm64-v8a/` directory. Spawns asynchronous cloud transfers without external root or Termux dependencies.
- **Automated Cloud Sync on Completion:**
  Patched Dalvik smali bytecode hooks into `DownloaderImpl$download$1` to instantly trigger background sync to Terabox, Google Drive, or Crypt Vaults once a media task reaches `Task$DownloadState$Completed`.
- **Automatic Tor Onion Routing:**
  Patched `DownloadPreferences` dynamically hooks into `tor_enabled` preference to route all stream resolution and downloads through local SOCKS5 proxy (`socks5://127.0.0.1:9050` / Orbot).
- **Zero-Knowledge AES-256 Crypt Vaults:**
  Enables client-side encryption of file contents and filenames before they leave the Android device.

---

## 📦 Download Prebuilt APK

Download the latest signed release directly from GitHub Releases:

👉 **[Download zytor-sovereign-v1.2.0.apk (GitHub Releases)](https://github.com/mayankreseracher/Z.Dip/releases/latest)**

### APK Verification & Integrity

| Property | Value |
|---|---|
| **Package Name** | `com.imkkingshuk.zytor` |
| **Version** | `1.2.0-sovereign` |
| **Target SDK** | Android 7.0+ (API 24 through Android 15) |
| **Architecture** | ARM64 (`arm64-v8a`) |
| **Signature Schemes** | APK Signature Scheme V1, V2, and V3 |
| **SHA-256** | `4c542338a5b91bd88fd6dca37b2e34edcb1a4c49d7f7184c72fdecfc1db813b1` |

---

## 🛠️ Included Smali Patches (`patches/`)

The `patches/` folder contains clean source-level patches and smali classes:

1. **[`BcloneCloudUploader.smali`](patches/BcloneCloudUploader.smali)**:
   New Dalvik class responsible for creating the default `bclone.conf` config, reading cloud preferences, locating `libbclone.so`, and spawning the background process.
2. **[`DownloaderImpl.smali.patch`](patches/DownloaderImpl.smali.patch)**:
   Unified diff hooking `BcloneCloudUploader.uploadIfEnabled()` when a download finishes.
3. **[`DownloadPreferences.patch`](patches/DownloadPreferences.patch)**:
   Unified diff patching `getProxy()` and `getProxyUrl()` to auto-route via Tor SOCKS5 when Tor is enabled.
4. **[`strings.xml.patch`](patches/strings.xml.patch)**:
   Localizes UI strings for cloud remotes, Terabox, Crypt vaults, and Tor routing.

---

## 🔧 Building & Re-patching from Source

To build a fresh Sovereign APK using the automated tool:

```bash
python android/tools/patch_apk.py \
    --source path/to/zytor_v1.2.0.apk \
    --output path/to/zytor-sovereign-v1.2.0.apk \
    --bclone-bin path/to/libbclone.so \
    --keystore path/to/debug.keystore
```

---

## 📲 Installation Instructions

### Via ADB
```bash
adb install -r zytor-sovereign-v1.2.0.apk
```

### Direct on Device
1. Download the APK file on your Android device.
2. Open your device file manager, tap the APK, and confirm installation.
3. Launch **Zytor Sovereign**.
4. Navigate to **Settings > Cloud Storage (bclone)** to select your cloud remote or **Settings > TOR** to enable onion anonymity.

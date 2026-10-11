# ☁️ Cloud Storage & Zero-Knowledge Crypt Vaults

**Z.Dip** natively integrates **bclone** (an advanced fork of rclone) to support direct-to-cloud streaming, post-download synchronization, and client-side AES-256 zero-knowledge encryption.

---

## 🌐 Supported Cloud Storage Backends

| Provider | Backend Identifier | Features |
|---|---|---|
| **Terabox** | `terabox` | 1TB+ Free Tier, direct upload, bclone native |
| **Google Drive** | `drive` | OAuth2, Team Drives, high speed |
| **Microsoft OneDrive** | `onedrive` | Personal & SharePoint business storage |
| **Mega.nz** | `mega` | Free and pro encrypted accounts |
| **Amazon S3 / R2 / MinIO** | `s3` | High-throughput object storage, S3 API |
| **WebDAV / Nextcloud** | `webdav` | Self-hosted storage instances |
| **AList / AllDebrid** | `alist` / `alldebrid` | Multi-cloud aggregator & debrid caches |
| **TelDrive** | `teldrive` | Unlimited cloud storage backed by Telegram |
| **SFTP / FTP** | `sftp` / `ftp` | Secure remote servers & NAS storage |
| **AES-256 Crypt Vault** | `crypt` | **Zero-Knowledge Client-Side Encryption** |

---

## 🔐 Zero-Knowledge Crypt Vaults

A **Crypt Vault** wraps any standard cloud storage remote (e.g. Terabox, Google Drive, or WebDAV) with client-side encryption.

### How It Works
1. When a file is uploaded, the filename and file payload are encrypted with **AES-256-GCM** before sending across the network.
2. The remote cloud provider sees only randomized ciphertext (e.g. `1b3a4f89d...`).
3. Only machines with the matching passphrase and salt can read or list decrypted files.

### Creating a Crypt Vault via Web Dashboard
1. Open the Z.Dip Web Dashboard at `http://127.0.0.1:8088`.
2. Navigate to **Cloud Remotes > Create Crypt Vault**.
3. Select your underlying base remote (e.g. `terabox`).
4. Enter your vault name (e.g. `my_vault`), strong password, and optional salt.
5. Click **Deploy Crypt Vault**.

### Creating a Crypt Vault via CLI
```bash
# In bclone.conf format:
[my_vault]
type = crypt
remote = terabox:/EncryptedMedia
filename_encryption = standard
directory_name_encryption = true
password = ***
```

---

## 🚀 Storage Delivery Modes

Z.Dip supports 3 distinct storage modes for every download:

1. **Local Disk (`local`)**:
   Downloads directly to the local machine (`/downloads`).
2. **Staged Cloud Sync (`sync_copy`)**:
   Downloads to local disk using maximum TurboBolt 64-segment speed, then asynchronously transfers to the cloud remote. Optionally purges the local file after upload is verified.
3. **Direct-to-Cloud Zero-Disk Streaming (`direct_stream`)**:
   Streams network media packets directly through the `bclone rcat` pipe into the remote cloud destination—**consuming zero bytes of physical local drive space**. Ideal for downloading 50GB+ 4K files on VPS instances or laptops with low storage!

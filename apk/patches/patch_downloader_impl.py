import os
import subprocess

file_path = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloaderImpl$download$1.smali"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = "invoke-static {p0, v0, v4}, Lcom/imkkingshuk/zytor/core/data/repository/DownloaderImpl;->access$setDownloadState(Lcom/imkkingshuk/zytor/core/data/repository/DownloaderImpl;Lcom/imkkingshuk/zytor/core/data/model/Task;Lcom/imkkingshuk/zytor/core/data/model/Task$DownloadState;)V"

replacement = target + """

    # Bclone cloud uploader trigger
    invoke-static {p0}, Lcom/imkkingshuk/zytor/core/data/repository/DownloaderImpl;->access$getAppContext$p(Lcom/imkkingshuk/zytor/core/data/repository/DownloaderImpl;)Landroid/content/Context;

    move-result-object v4

    invoke-static {v4, v3}, Lcom/imkkingshuk/zytor/core/cloud/BcloneCloudUploader;->uploadIfEnabled(Landroid/content/Context;Ljava/lang/String;)V
"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched DownloaderImpl$download$1.smali")
else:
    print("Target string not found in DownloaderImpl$download$1.smali")

res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", file_path, "-o", "/tmp/test_download.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

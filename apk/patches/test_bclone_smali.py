import os
import subprocess

smali_code = """
.class public final Lcom/imkkingshuk/zytor/core/cloud/BcloneCloudUploader;
.super Ljava/lang/Object;
.source "BcloneCloudUploader.java"

# static fields
.field private static final TAG:Ljava/lang/String; = "BcloneCloudUploader"


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static final ensureDefaultConfig(Landroid/content/Context;)V
    .locals 3

    if-nez p0, :cond_start

    return-void

    :cond_start
    :try_start_0
    new-instance v0, Ljava/io/File;

    invoke-virtual {p0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object p0

    const-string v1, "bclone.conf"

    invoke-direct {v0, p0, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result p0

    if-nez p0, :cond_done

    new-instance p0, Ljava/io/FileWriter;

    invoke-direct {p0, v0}, Ljava/io/FileWriter;-><init>(Ljava/io/File;)V

    const-string v0, "# Zytor Sovereign Cloud Storage (bclone)\\n[terabox]\\ntype = terabox\\n\\n[vault]\\ntype = crypt\\nremote = terabox:/ZytorEncrypted\\nfilename_encryption = standard\\ndirectory_name_encryption = true\\n\\n[gdrive]\\ntype = drive\\nscope = drive\\n"

    invoke-virtual {p0, v0}, Ljava/io/Writer;->write(Ljava/lang/String;)V

    invoke-virtual {p0}, Ljava/io/OutputStreamWriter;->close()V

    const-string p0, "BcloneCloudUploader"

    const-string v0, "Default bclone.conf created successfully"

    invoke-static {p0, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catch_err

    goto :cond_done

    :catch_err
    move-exception p0

    const-string v0, "BcloneCloudUploader"

    const-string v1, "Failed to create default bclone.conf"

    invoke-static {v0, v1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    :cond_done
    return-void
.end method

.method public static final uploadIfEnabled(Landroid/content/Context;Ljava/lang/String;)V
    .locals 8

    if-eqz p0, :cond_exit

    if-nez p1, :cond_check_empty

    return-void

    :cond_check_empty
    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_check_pref

    return-void

    :cond_check_pref
    :try_start_0
    invoke-static {p0}, Lcom/imkkingshuk/zytor/core/cloud/BcloneCloudUploader;->ensureDefaultConfig(Landroid/content/Context;)V

    const-string v0, "bclone_enabled"

    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getBoolean(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_pref_ok

    const-string v0, "web3_enabled"

    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getBoolean(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_pref_ok

    return-void

    :cond_pref_ok
    const-string v0, "bclone_remote"

    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_remote_fallback

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_remote_ok

    :cond_remote_fallback
    const-string v0, "web3_provider"

    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_remote_default

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_remote_ok

    :cond_remote_default
    const-string v0, "terabox:"

    :cond_remote_ok
    const-string v1, "bclone_dest_path"

    invoke-static {v1}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    if-eqz v1, :cond_dest_default

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_dest_ok

    :cond_dest_default
    const-string v1, "/ZytorDownloads"

    :cond_dest_ok
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationInfo()Landroid/content/pm/ApplicationInfo;

    move-result-object v2

    iget-object v2, v2, Landroid/content/pm/ApplicationInfo;->nativeLibraryDir:Ljava/lang/String;

    new-instance v3, Ljava/io/File;

    const-string v4, "libbclone.so"

    invoke-direct {v3, v2, v4}, Ljava/io/File;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->exists()Z

    move-result v2

    if-nez v2, :cond_start_upload

    const-string p0, "BcloneCloudUploader"

    const-string p1, "libbclone.so not found in nativeLibraryDir"

    invoke-static {p0, p1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return-void

    :cond_start_upload
    const-string v2, ":"

    invoke-virtual {v0, v2}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_format_target

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    goto :goto_target

    :cond_format_target
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, ":"

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_target
    const-string v1, "BcloneCloudUploader"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Initiating cloud transfer: "

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v4, " -> "

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v1, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    invoke-virtual {v3}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    const-string v2, "copy"

    invoke-virtual {v1, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    invoke-virtual {v1, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    invoke-virtual {v1, v0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    new-instance p1, Ljava/io/File;

    invoke-virtual {p0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object p0

    const-string v0, "bclone.conf"

    invoke-direct {p1, p0, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->exists()Z

    move-result p0

    if-eqz p0, :cond_launch

    const-string p0, "--config"

    invoke-virtual {v1, p0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    invoke-virtual {p1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v1, p0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    :cond_launch
    new-instance p0, Ljava/lang/ProcessBuilder;

    invoke-direct {p0, v1}, Ljava/lang/ProcessBuilder;-><init>(Ljava/util/List;)V

    const/4 p1, 0x1

    invoke-virtual {p0, p1}, Ljava/lang/ProcessBuilder;->redirectErrorStream(Z)Ljava/lang/ProcessBuilder;

    invoke-virtual {p0}, Ljava/lang/ProcessBuilder;->start()Ljava/lang/Process;

    const-string p0, "BcloneCloudUploader"

    const-string p1, "bclone process spawned successfully in background"

    invoke-static {p0, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catch_err

    goto :cond_exit

    :catch_err
    move-exception p0

    const-string p1, "BcloneCloudUploader"

    const-string v0, "Failed to upload file via bclone"

    invoke-static {p1, v0, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    :cond_exit
    return-void
.end method
"""

target_dir = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/cloud"
os.makedirs(target_dir, exist_ok=True)
smali_path = os.path.join(target_dir, "BcloneCloudUploader.smali")
with open(smali_path, "w", encoding="utf-8") as f:
    f.write(smali_code.strip() + "\n")

print("Written BcloneCloudUploader.smali")
res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", smali_path, "-o", "/tmp/test.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

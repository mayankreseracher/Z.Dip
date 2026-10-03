import os
import subprocess

file_path = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali"

# Restore original by reversing or reloading
res = subprocess.run(["git", "checkout", file_path], cwd="/home/insectoid/apk_build/zytor_decompiled", capture_output=True, text=True)
if res.returncode != 0:
    # Not a git repo, let's restore from original decompiled if needed or clean up
    with open(file_path, "r", encoding="utf-8") as f:
        c = f.read()
    # Remove previous injected block
    start_tag = "# Auto-route through Tor Onion Routing"
    end_tag = ":cond_zytor_skip_tor\n"
    if start_tag in c:
        p1 = c.find(start_tag)
        p2 = c.find(end_tag) + len(end_tag)
        c = c[:p1] + c[p2:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(c)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = '    const-string v2, "proxy_url"\n\n    .line 279\n    .line 280\n    invoke-static {v1, v2, v5, v4, v5}, Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;->getStringValue$default(Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;\n\n    .line 281\n    .line 282\n    .line 283\n    move-result-object v47\n'

injection = """
    # Auto-route through Tor Onion Routing if tor_enabled is true
    iget-object v1, v0, Lcom/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository;->preferenceUtil:Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;
    const-string v2, "tor_enabled"
    invoke-static {v1, v2, v3, v4, v5}, Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;->getBooleanValue$default(Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;Ljava/lang/String;ZILjava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_zytor_skip_tor
    const/4 v1, 0x1
    move v46, v1
    iget-object v1, v0, Lcom/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository;->preferenceUtil:Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;
    const-string v2, "tor_proxy_address"
    invoke-static {v1, v2, v5, v4, v5}, Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;->getStringValue$default(Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;
    move-result-object v1
    if-nez v1, :cond_zytor_check_tor_empty
    const-string v1, "socks5://127.0.0.1:9050"
    move-object v47, v1
    goto :cond_zytor_skip_tor
    :cond_zytor_check_tor_empty
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z
    move-result v2
    if-eqz v2, :cond_zytor_use_custom_tor
    const-string v1, "socks5://127.0.0.1:9050"
    :cond_zytor_use_custom_tor
    move-object v47, v1
    :cond_zytor_skip_tor
"""

replacement = target + injection
if target in content:
    content = content.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched cleanly!")
else:
    print("Target not found!")

res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", file_path, "-o", "/tmp/test_pref_repo.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

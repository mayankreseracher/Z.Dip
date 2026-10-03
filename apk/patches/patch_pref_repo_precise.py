import os
import subprocess

file_path = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali"
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
    const/16 v46, 0x1
    iget-object v1, v0, Lcom/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository;->preferenceUtil:Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;
    const-string v2, "tor_proxy_address"
    invoke-static {v1, v2, v5, v4, v5}, Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;->getStringValue$default(Lcom/imkkingshuk/zytor/core/common/PreferenceUtil;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;
    move-result-object v47
    if-nez v47, :cond_zytor_check_tor_empty
    const-string v47, "socks5://127.0.0.1:9050"
    goto :cond_zytor_skip_tor
    :cond_zytor_check_tor_empty
    invoke-virtual {v47}, Ljava/lang/String;->isEmpty()Z
    move-result v1
    if-eqz v1, :cond_zytor_skip_tor
    const-string v47, "socks5://127.0.0.1:9050"
    :cond_zytor_skip_tor
"""

replacement = target + injection

if target in content:
    content = content.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched DownloadPreferencesRepository.smali")
else:
    print("Target not found!")

res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", file_path, "-o", "/tmp/test_pref_repo.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

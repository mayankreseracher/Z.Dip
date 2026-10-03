import subprocess

file_path = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/models/DownloadPreferences.smali"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace getProxy()
start_p = text.find('.method public final getProxy()Z')
end_p = text.find('.end method', start_p) + 11

new_get_proxy = """.method public final getProxy()Z
    .locals 2

    iget-boolean v0, p0, Lcom/imkkingshuk/zytor/core/models/DownloadPreferences;->proxy:Z
    if-eqz v0, :cond_check_tor

    const/4 v0, 0x1
    return v0

    :cond_check_tor
    const-string v0, "tor_enabled"
    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getBoolean(Ljava/lang/String;)Z
    move-result v0
    return v0
.end method"""

text = text[:start_p] + new_get_proxy + text[end_p:]

# Replace getProxyUrl()
start_u = text.find('.method public final getProxyUrl()Ljava/lang/String;')
end_u = text.find('.end method', start_u) + 11

new_get_proxy_url = """.method public final getProxyUrl()Ljava/lang/String;
    .locals 2

    iget-boolean v0, p0, Lcom/imkkingshuk/zytor/core/models/DownloadPreferences;->proxy:Z
    if-eqz v0, :cond_check_tor

    iget-object v0, p0, Lcom/imkkingshuk/zytor/core/models/DownloadPreferences;->proxyUrl:Ljava/lang/String;
    if-eqz v0, :cond_check_tor
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z
    move-result v1
    if-nez v1, :cond_check_tor
    return-object v0

    :cond_check_tor
    const-string v0, "tor_enabled"
    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getBoolean(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_ret_default

    const-string v0, "tor_proxy_address"
    invoke-static {v0}, Lcom/imkkingshuk/zytor/core/common/PreferenceExtensionsKt;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :cond_tor_fallback
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z
    move-result v1
    if-nez v1, :cond_tor_fallback
    return-object v0

    :cond_tor_fallback
    const-string v0, "socks5://127.0.0.1:9050"
    return-object v0

    :cond_ret_default
    iget-object v0, p0, Lcom/imkkingshuk/zytor/core/models/DownloadPreferences;->proxyUrl:Ljava/lang/String;
    return-object v0
.end method"""

text = text[:start_u] + new_get_proxy_url + text[end_u:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Patched DownloadPreferences.smali successfully!")

res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", file_path, "-o", "/tmp/test_pref_model.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

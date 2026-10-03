with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/YtDlpEngine$execute$1.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "const-string" in line or "invoke" in line or "ProcessBuilder" in line or "exec" in line:
        if any(w in line for w in ["Process", "proxy", "aria2c", "socks", "execute", "start", "command", "builder", "Environment"]):
            print(line.strip())

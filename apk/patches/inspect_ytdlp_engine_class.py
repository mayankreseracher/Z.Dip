with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/YtDlpEngine.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "const-string" in line or "invoke-virtual" in line and any(k in line for k in ["python", "quickjs", "execute", "Process"]):
        print(line.strip()[:100])

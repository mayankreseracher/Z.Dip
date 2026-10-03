with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/YtDlpEngine.smali") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "getPythonPath" in line or "getYtDlpPath" in line:
        for i in range(max(0, idx - 10), min(len(lines), idx + 25)):
            print(f"{i}: {lines[i].rstrip()}")
        print("-" * 50)

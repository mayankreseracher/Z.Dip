import re

filename = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/network/YoutubeDLManager$downloadVideo$2.smali"
with open(filename, "r", encoding="utf-8") as f:
    text = f.read()

print("File size:", len(text))
for line in text.splitlines():
    if any(k in line.lower() for k in ['proxy', 'tor', 'aria2c', 'turbo', 'request', 'ytdlprequest', 'output']):
        print(line.strip()[:120])

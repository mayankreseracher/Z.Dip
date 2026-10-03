with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/util/DownloadUtil.smali") as f:
    text = f.read()

print("File size:", len(text))
for line in text.splitlines():
    if any(k in line.lower() for k in ['proxy', 'ytdlprequest', 'build', 'request', 'aria2c', 'turbobolt']):
        print(line.strip()[:120])

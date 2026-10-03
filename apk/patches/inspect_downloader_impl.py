with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloaderImpl.smali") as f:
    text = f.read()

print("File size:", len(text))
for line in text.splitlines():
    if line.startswith(".method") or line.startswith(".field"):
        print(line.strip()[:100])

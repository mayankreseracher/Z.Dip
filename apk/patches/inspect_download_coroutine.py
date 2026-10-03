with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloaderImpl$download$1.smali") as f:
    text = f.read()

print("File size:", len(text))
for line in text.splitlines():
    if any(k in line for k in ['invoke', 'const-string', 'Completed', 'Error', 'State']):
        print(line.strip()[:120])

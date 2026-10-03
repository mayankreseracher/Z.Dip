with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali") as f:
    lines = f.readlines()

for i in range(2500, 2755):
    if lines[i].startswith(".method") or "tor" in lines[i].lower() or "proxy" in lines[i].lower():
        print(f"{i}: {lines[i].rstrip()}")

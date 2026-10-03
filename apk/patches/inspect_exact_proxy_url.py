with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '"proxy_url"' in line:
        for i in range(idx - 10, idx + 20):
            print(repr(lines[i]))
        break

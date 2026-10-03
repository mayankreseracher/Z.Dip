with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali") as f:
    text = f.read()

for line in text.splitlines():
    if any(k in line for k in ["tor", "proxy", "DownloadPreferences", "PreferenceUtil"]):
        print(line.strip()[:100])

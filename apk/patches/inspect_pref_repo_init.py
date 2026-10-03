with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "Lcom/imkkingshuk/zytor/core/models/DownloadPreferences;-><init>(" in line:
        for i in range(max(0, idx - 30), min(len(lines), idx + 10)):
            print(f"{i}: {lines[i].rstrip()}")
        print("="*60)

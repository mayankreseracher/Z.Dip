with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/util/DownloadUtil.smali") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "enableProxy" in line:
        for i in range(max(0, idx - 15), min(len(lines), idx + 20)):
            print(f"{i}: {lines[i].rstrip()}")
        print("=" * 50)

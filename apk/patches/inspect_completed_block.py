with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloaderImpl$download$1.smali") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "Task$DownloadState$Completed" in line:
        start = max(0, idx - 25)
        end = min(len(lines), idx + 40)
        for i in range(start, end):
            print(f"{i}: {lines[i].rstrip()}")
        break

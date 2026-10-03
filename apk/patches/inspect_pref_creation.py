with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali") as f:
    text = f.read()

start = text.find('new-instance')
while start != -1:
    end = text.find('\n', start)
    line = text[start:end]
    if 'DownloadPreferences' in line:
        context_start = max(0, start - 200)
        context_end = min(len(text), start + 800)
        print(text[context_start:context_end])
        print("="*60)
        break
    start = text.find('new-instance', start + 1)

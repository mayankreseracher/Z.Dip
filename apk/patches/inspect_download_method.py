with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloaderImpl.smali") as f:
    text = f.read()

start = text.find('.method private final download(Lcom/imkkingshuk/zytor/core/data/model/Task;)V')
end = text.find('.end method', start)
print(text[start:end+11])

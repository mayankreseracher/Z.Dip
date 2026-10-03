with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/network/YoutubeDLManager$downloadVideo$2.smali") as f:
    text = f.read()

start = text.find('.method private static final invokeSuspend$lambda$0')
end = text.find('.end method', start)
print(text[start:end+11])

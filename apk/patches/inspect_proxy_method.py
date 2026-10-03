with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/YtDlpRequest.smali") as f:
    text = f.read()

start = text.find('.method public final proxy')
end = text.find('.end method', start)
print(text[start:end+11])

with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/models/DownloadPreferences.smali") as f:
    text = f.read()

start = text.find('.method public final getProxy()Z')
end = text.find('.end method', start)
print(text[start:end+11])

start = text.find('.method public final getProxyUrl()Ljava/lang/String;')
end = text.find('.end method', start)
print(text[start:end+11])

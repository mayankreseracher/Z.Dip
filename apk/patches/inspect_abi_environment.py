with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/abi/AbiManager.smali") as f:
    text = f.read()

start = text.find('.method public final getEnvironment()Ljava/util/Map;')
end = text.find('.end method', start)
print(text[start:end+11])

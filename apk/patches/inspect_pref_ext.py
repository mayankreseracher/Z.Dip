with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/common/PreferenceExtensionsKt.smali") as f:
    text = f.read()

for line in text.splitlines():
    if line.startswith(".method"):
        print(line)

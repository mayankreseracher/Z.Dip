with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/abi/AbiManager.smali") as f:
    text = f.read()

for line in text.splitlines():
    if any(k in line for k in ["nativeLibraryDir", "getNativeLibraryDir", "libaria2c", "libpython", "packages", "getAria2cPath"]):
        print(line.strip()[:100])

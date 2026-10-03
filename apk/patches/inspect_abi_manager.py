with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/allinonemodule/ytdlp/abi/AbiManager.smali") as f:
    lines = f.readlines()

for line in lines:
    if line.startswith(".method") or line.startswith(".field") or "const-string" in line:
        print(line.strip())

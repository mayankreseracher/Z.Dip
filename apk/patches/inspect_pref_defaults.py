with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/common/PreferenceUtil.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "tor_proxy_address" in line:
        print(line.strip())

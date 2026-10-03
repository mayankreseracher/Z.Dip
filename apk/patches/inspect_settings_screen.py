with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/feature/settings/SettingsScreenKt.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "settings/" in line or "const-string" in line or "R$string" in line:
        print(line.strip()[:100])

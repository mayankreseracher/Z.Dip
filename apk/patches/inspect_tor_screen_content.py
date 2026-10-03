with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/feature/tor/ComposableSingletons$TorScreenKt.smali") as f:
    text = f.read()

print("File size:", len(text))
for line in text.splitlines():
    if "const-string" in line or "R$string" in line or "R$drawable" in line:
        print(line.strip()[:100])

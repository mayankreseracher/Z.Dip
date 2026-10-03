with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/navigation/ComposableSingletons$ZytorNavHostKt.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "Tor" in line or "Torrent" in line or "nav" in line.lower() or "route" in line.lower():
        print(line.strip()[:100])

with open("/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/feature/torrent/ComposableSingletons$TorrentScreenKt.smali") as f:
    text = f.read()

for line in text.splitlines():
    if "R$string" in line or "const-string" in line:
        print(line.strip()[:100])

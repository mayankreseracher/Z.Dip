xml_path = "/home/insectoid/apk_build/zytor_decompiled/res/values/strings.xml"
with open(xml_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<string name="coming_soon">Coming soon!</string>',
    '<string name="coming_soon">Sovereign Engine Active &amp; Protected</string>'
)
content = content.replace(
    '<string name="torrent_desc">This page will provide tools for downloading and managing torrent files.</string>',
    '<string name="torrent_desc">BitTorrent and Metalink high-speed engine powered by aria2c &amp; TurboBolt. Configure connections, DHT, and limits in Settings &gt; Torrent.</string>'
)

with open(xml_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated coming_soon and torrent_desc in strings.xml")

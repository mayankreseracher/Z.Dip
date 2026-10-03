import os
import glob
import re

base_dir = "/home/insectoid/apk_build/zytor_decompiled"

def search_text(pattern, path_glob):
    regex = re.compile(pattern, re.IGNORECASE)
    for p in glob.glob(os.path.join(base_dir, path_glob), recursive=True):
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = regex.findall(content)
                if matches:
                    print(f"File: {p}")
                    for line in content.splitlines():
                        if regex.search(line):
                            print(f"  {line.strip()}")

print("=== TOR / TORRENT FILES ===")
search_text(r"coming soon|under development|tor_proxy|onion|proxy", "smali_classes3/com/imkkingshuk/zytor/feature/**/*.smali")

print("\n=== DOWNLOAD SETTINGS / YTDLP REQ ===")
search_text(r"proxy|tor|aria2|turbo", "smali_classes3/com/imkkingshuk/zytor/allinonemodule/**/*.smali")

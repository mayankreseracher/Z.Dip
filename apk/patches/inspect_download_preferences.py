import glob

files = glob.glob('/home/insectoid/apk_build/zytor_decompiled/**/DownloadPreferences.smali', recursive=True)
print("Files:", files)
if files:
    with open(files[0]) as f:
        text = f.read()
    for line in text.splitlines():
        if line.startswith(".field") or line.startswith(".method public final get"):
            print(line)

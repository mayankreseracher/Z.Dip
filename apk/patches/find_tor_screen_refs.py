import glob

files = glob.glob('/home/insectoid/apk_build/zytor_decompiled/smali*/**/*.smali', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
        if 'TorScreenKt' in c:
            print(f)

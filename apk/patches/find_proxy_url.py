import glob, os

files = glob.glob('/home/insectoid/apk_build/zytor_decompiled/smali*/**/*.smali', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
        if 'proxy_url' in c or 'PROXY_URL' in c:
            print(f)

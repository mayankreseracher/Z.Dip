import zipfile
import subprocess
import shutil
import os

apk_path = "/mnt/c/Users/Mayank/Documents/Tiger underneath/zytor_v1.2.0.apk"
with zipfile.ZipFile(apk_path, "r") as z:
    z.extract("classes3.dex", "/tmp")

print("Extracted classes3.dex")
subprocess.run(["java", "-jar", "/home/insectoid/apk_build/baksmali.jar", "d", "/tmp/classes3.dex", "-o", "/tmp/fresh_smali"], check=True)
print("Baksmali decoded classes3.dex")

src = "/tmp/fresh_smali/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali"
dst = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali"
shutil.copyfile(src, dst)
print("Restored DownloadPreferencesRepository.smali, size:", os.path.getsize(dst))

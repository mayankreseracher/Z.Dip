import os
import subprocess

file_path = "/home/insectoid/apk_build/zytor_decompiled/smali_classes3/com/imkkingshuk/zytor/core/data/repository/DownloadPreferencesRepository.smali"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the second duplicate block and remove it
new_lines = []
skip = False
for idx, line in enumerate(lines):
    if idx >= 2604 and "const/4 v1, 0x1" in line:
        skip = True
    if skip:
        if idx > 2620 and ":cond_zytor_skip_tor" in line:
            skip = False
            continue
        continue
    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed duplicate block!")
res = subprocess.run(["java", "-jar", "/home/insectoid/apk_build/smali.jar", "a", file_path, "-o", "/tmp/test_pref_repo.dex"], capture_output=True, text=True)
print("Smali assemble returncode:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)

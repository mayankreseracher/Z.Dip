import os
import shutil

root_dir = r"c:\Users\Mayank\Documents\Tiger underneath"
target_dir = os.path.join(root_dir, "Zytor-Sovereign")

os.makedirs(os.path.join(target_dir, "apk", "patches"), exist_ok=True)
os.makedirs(os.path.join(target_dir, "engine"), exist_ok=True)

print("Target dir created:", target_dir)

# Copy APK
apk_src = os.path.join(root_dir, "zytor-sovereign-v1.2.0.apk")
apk_dst = os.path.join(target_dir, "apk", "zytor-sovereign-v1.2.0.apk")
if os.path.exists(apk_src):
    shutil.copyfile(apk_src, apk_dst)
    print("Copied APK to:", apk_dst)

# Copy Smali patches & scripts from scratch
scratch_dir = r"C:\Users\Mayank\.gemini\antigravity\brain\384036dd-50d0-481c-a40a-dcecb34a9556\scratch"
if os.path.exists(scratch_dir):
    for f in os.listdir(scratch_dir):
        if f.endswith(".py") or f.endswith(".smali"):
            shutil.copyfile(
                os.path.join(scratch_dir, f),
                os.path.join(target_dir, "apk", "patches", f)
            )
    print("Copied APK patches & scripts")

# Copy engine
engine_src = os.path.join(root_dir, "zytor-engine")
engine_dst = os.path.join(target_dir, "engine")

if os.path.exists(engine_src):
    for item in os.listdir(engine_src):
        s = os.path.join(engine_src, item)
        d = os.path.join(engine_dst, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copyfile(s, d)
    print("Copied Zytor Engine files")

print("Zytor-Sovereign package structure successfully generated.")

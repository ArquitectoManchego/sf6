import zipfile
import os
import sys

ZIP_PATH = r"C:\Users\Alex\Downloads\[Telegram PlayStation Pulse] DLCs Street Fighter 6 CUSA31498 EUR.zip"
TARGET_DIR = r"E:\SF6_EXTRACTED"
TARGET_FILE = "CUSA31498.Street.Fighter.6-Fighting.Ground-CyB1K.pkg"
OUT_PKG = os.path.join(TARGET_DIR, "FightingGround.pkg")

os.makedirs(TARGET_DIR, exist_ok=True)

print(f"Opening ZIP: {ZIP_PATH}")
with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    target_entry = None
    for name in z.namelist():
        if "Fighting.Ground" in name and name.endswith(".pkg"):
            target_entry = name
            break
            
    if not target_entry:
        print("Fighting.Ground PKG not found in ZIP!")
        sys.exit(1)
        
    print(f"Extracting '{target_entry}' to '{OUT_PKG}'...")
    with z.open(target_entry) as source, open(OUT_PKG, 'wb') as dest:
        buf_size = 1024 * 1024 * 16  # 16 MB chunks
        copied = 0
        total = z.getinfo(target_entry).file_size
        while True:
            chunk = source.read(buf_size)
            if not chunk:
                break
            dest.write(chunk)
            copied += len(chunk)
            if copied % (1024 * 1024 * 256) < buf_size:
                print(f"Progress: {copied / (1024*1024):.1f} / {total / (1024*1024):.1f} MB ({copied/total*100:.1f}%)")

print("Extraction completed successfully!")

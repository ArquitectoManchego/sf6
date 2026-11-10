import os
import glob

FG_DIR = r"E:\SF6_EXTRACTED\FightingGround_Data"

exts = {}
char_files = {}

for root, dirs, files in os.walk(FG_DIR):
    for f in files:
        # Get extension
        parts = f.split('.')
        ext = ".".join(parts[1:]) if len(parts) > 1 else "none"
        ext_base = parts[1] if len(parts) > 1 else "none"
        exts[ext_base] = exts.get(ext_base, 0) + 1
        
        # Check character
        lower = f.lower()
        full_path = os.path.join(root, f)
        for c in ['esf004', 'esf006', 'esf007', 'esf008', 'esf010', 'esf011', 'esf021']:
            if c in lower or c in root.lower():
                char_files[c] = char_files.get(c, 0) + 1

print("=== EXTENSION SUMMARY IN FIGHTING GROUND DATA ===", flush=True)
for ext, count in sorted(exts.items(), key=lambda x: -x[1])[:20]:
    print(f"  .{ext:15}: {count:5} files", flush=True)

print("\n=== CHARACTER FILE COUNTS IN FIGHTING GROUND DATA ===", flush=True)
for char, count in sorted(char_files.items()):
    print(f"  {char:10}: {count:5} files", flush=True)

# Print some mesh files
print("\n=== SAMPLE MESH FILES ===", flush=True)
meshes = []
for root, dirs, files in os.walk(FG_DIR):
    for f in files:
        if "mesh" in f.lower():
            meshes.append(os.path.join(root, f))
            if len(meshes) >= 15:
                break
    if len(meshes) >= 15:
        break

for m in meshes:
    rel = os.path.relpath(m, FG_DIR)
    print(f"  {rel}", flush=True)

# Print some motlist / animation files
print("\n=== SAMPLE ANIMATION / MOTLIST FILES ===", flush=True)
mots = []
for root, dirs, files in os.walk(FG_DIR):
    for f in files:
        if "motlist" in f.lower() or "mot." in f.lower():
            mots.append(os.path.join(root, f))
            if len(mots) >= 15:
                break
    if len(mots) >= 15:
        break

for m in mots:
    rel = os.path.relpath(m, FG_DIR)
    print(f"  {rel}", flush=True)


import os
import subprocess

base_dir = r"raw_assets\dread_suit_samus\Dread Suit Samus\Samus Dread Suit\fighter\samus\model\body"
conv_exe = r"tools\ultimate_tex\ultimate_tex_cli.exe"

slots = ["c00", "c01", "c02", "c03"]

for slot in slots:
    slot_dir = os.path.join(base_dir, slot)
    if os.path.exists(slot_dir):
        print(f"--- Converting textures for {slot} ---")
        textures = [
            ("met_samus_001_col.nutexb", "samus_col.png"),
            ("met_samus_001_emi.nutexb", "samus_emi.png"),
            ("met_samus_001_nor.nutexb", "samus_nor.png"),
            ("met_samus_001_prm.nutexb", "samus_prm.png"),
            ("met_morph_001_col.nutexb", "morph_col.png")
        ]
        for src, dst in textures:
            src_p = os.path.join(slot_dir, src)
            dst_p = os.path.join(slot_dir, dst)
            if os.path.exists(src_p):
                cmd = [conv_exe, src_p, dst_p]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if os.path.exists(dst_p):
                    print(f"  Converted {src} -> {dst} ({os.path.getsize(dst_p)} bytes)")
                else:
                    print(f"  Failed {src}: {res.stderr}")

print("ALL SAMUS TEXTURES CONVERTED!")

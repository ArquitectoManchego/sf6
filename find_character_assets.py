import re
import collections

LIST_PATH = r"c:\PROYECTOS ANTIGRAVITY\sf6\tools\retool\SF6_PS4_Release.list"

chars = {
    'esf004': 'Chun-Li',
    'esf006': 'Cammy',
    'esf007': 'Kimberly',
    'esf008': 'Lily',
    'esf010': 'Juri',
    'esf011': 'Marisa',
    'esf021': 'A.K.I.'
}

results = collections.defaultdict(lambda: collections.defaultdict(list))

with open(LIST_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        line = line.strip()
        lower = line.lower()
        for c_code, c_name in chars.items():
            if c_code in lower:
                if '.mesh' in lower:
                    results[c_name]['mesh'].append(line)
                elif '.mdf2' in lower:
                    results[c_name]['mdf2'].append(line)
                elif '.motlist' in lower:
                    results[c_name]['motlist'].append(line)
                elif '.tex' in lower:
                    results[c_name]['tex'].append(line)
                elif '.chain' in lower:
                    results[c_name]['chain'].append(line)

print("=== ASSET BREAKDOWN BY CHARACTER IN STREET FIGHTER 6 (PS4) ===", flush=True)
for c_name, data in results.items():
    print(f"\n--- {c_name.upper()} ---", flush=True)
    print(f"  Meshes (.mesh)   : {len(data['mesh'])}", flush=True)
    print(f"  Materials (.mdf2): {len(data['mdf2'])}", flush=True)
    print(f"  Motlists (anim)  : {len(data['motlist'])}", flush=True)
    print(f"  Physics (.chain) : {len(data['chain'])}", flush=True)
    print(f"  Textures (.tex)  : {len(data['tex'])}", flush=True)
    if data['mesh']:
        print("  Sample Meshes:", flush=True)
        for m in data['mesh'][:4]:
            print(f"    - {m}", flush=True)

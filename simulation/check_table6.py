import json
import numpy as np

with open('quantum_walk_results.json') as f:
    data = json.load(f)['data']

classes = {}
for r in data:
    ctype = r['type']
    if ctype not in classes:
        classes[ctype] = []
    classes[ctype].append(r)

for ctype, rows in classes.items():
    mitm_ratio = [r['mitm'] / r['quantum_queries'] for r in rows]
    bb_ratio = [r['T_LP'] / r['quantum_queries'] for r in rows]
    bb_ratio2 = [r['quantum_queries'] / r['T_LP'] for r in rows]
    
    print(f"{ctype}:")
    print(f"  MitM/Q mean={np.mean(mitm_ratio):.1f} std={np.std(mitm_ratio):.1f}")
    print(f"  T_LP/Q mean={np.mean(bb_ratio):.1f} std={np.std(bb_ratio):.1f}")
    print(f"  Q/T_LP mean={np.mean(bb_ratio2):.1f} std={np.std(bb_ratio2):.1f}")

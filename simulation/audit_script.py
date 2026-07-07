import json

print("--- quantum_walk_results.json ---")
with open('quantum_walk_results.json', 'r') as f:
    qw = json.load(f)['data']
    for row in qw:
        if row['n'] in [12, 14]:
            print(f"{row['type']} n={row['n']}: T_LP={row.get('T_LP')}, Q_d={row.get('montanaro_queries_decisive')}, depth={row.get('depth')}")

print("\n--- benchmark_results.json ---")
try:
    with open('benchmark_results.json', 'r') as f:
        # Check structure
        bm = json.load(f)
        if isinstance(bm, dict) and 'data' in bm:
            bm = bm['data']
        for row in bm:
            if row.get('n') in [12, 24]:
                print(f"{row.get('type')} n={row.get('n')}: T_core={row.get('T_core')}, alpha={row.get('alpha', 'N/A')}")
except Exception as e:
    print("Error:", e)

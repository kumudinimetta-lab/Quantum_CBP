import json
import glob
import os

print("--- Checking all benchmark JSONs ---")
for file in glob.glob('benchmark*.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            if 'results' in data:
                print(f"{file} has {len(data['results'])} results.")
            elif isinstance(data, list):
                print(f"{file} is a list with {len(data)} items.")
    except Exception as e:
        pass

with open('quantum_walk_results.json', 'r') as f:
    qw = json.load(f)['data']
    print("\n--- Quantum Walk Q_d / sqrt(T_LP * m) checks ---")
    for r in qw:
        if r['n'] == 12:
            q_d = r.get('montanaro_queries_decisive')
            t_lp = r.get('T_LP')
            m = r.get('depth')
            if q_d and t_lp and m:
                print(f"{r['type']} n={r['n']} T_LP={t_lp} Q_d={q_d} m={m} ratio={q_d / (t_lp * m)**0.5:.2f}")


import json
import numpy as np
import math

with open('benchmark_results_v5_hard.json', 'r') as f:
    records = json.load(f).get('data', [])

for n in [20]:
    group = [r for r in records if r.get('type') == 'uncorrelated' and r.get('n') == n]
    
    # Let's test different average methods
    
    # 1. average of mitm / sqrt(T_core)
    avg1 = np.mean([ 2**(n/2) / math.sqrt(r.get('T_core', 1)) for r in group if r.get('T_core', 1) > 0])
    
    # 2. average of mitm / sqrt(T_core * m)
    avg2 = np.mean([ 2**(n/2) / math.sqrt(r.get('T_core', 1) * max(1, r.get('m', 1))) for r in group if r.get('T_core', 1) > 0])
    
    # 3. mitm / average(sqrt(T_core))
    avg3 = 2**(n/2) / np.mean([math.sqrt(r.get('T_core', 1)) for r in group])
    
    # 4. mitm / average(sqrt(T_core * m))
    avg4 = 2**(n/2) / np.mean([math.sqrt(r.get('T_core', 1) * r.get('m', 1)) for r in group])
    
    # 5. average of (T_full / sqrt(T_core * m))
    avg5 = np.mean([ r.get('T_full') / math.sqrt(r.get('T_core', 1) * max(1, r.get('m', 1))) for r in group if r.get('T_core', 1) > 0])
    
    print(f"n={20} avg1={avg1:.2f} avg2={avg2:.2f} avg3={avg3:.2f} avg4={avg4:.2f} avg5={avg5:.2f}")


import json
import numpy as np
from scipy import stats

def compute_ci(alphas):
    if len(alphas) < 2: return (np.nan, np.nan)
    mean = np.mean(alphas)
    sem = stats.sem(alphas)
    ci = stats.t.interval(0.95, len(alphas)-1, loc=mean, scale=sem)
    return ci

print("=== LARGE SCALE RAW ALPHA STATS ===")
try:
    with open('simulation/large_scale_alpha_raw.json') as f:
        data = json.load(f)
        
    classes = {}
    for r in data:
        cls = r['class']
        n = r['n']
        a = r['alpha']
        if cls not in classes: classes[cls] = {}
        if n not in classes[cls]: classes[cls][n] = []
        classes[cls][n].append(a)
        
    for cls, ns in classes.items():
        print(f"\n--- Class: {cls} ---")
        for n in sorted(ns.keys()):
            arr = np.array(ns[n])
            ci = compute_ci(arr)
            print(f"n={n:5} | N={len(arr)} | med={np.median(arr):.4f} | IQR={np.percentile(arr,75)-np.percentile(arr,25):.4f} | mean={np.mean(arr):.4f} | sd={np.std(arr):.4f} | min={np.min(arr):.4f} | max={np.max(arr):.4f} | 95% CI=[{ci[0]:.4f}, {ci[1]:.4f}]")
            
    print("\n--- Pooled Descriptive Summaries by n ---")
    pooled = {}
    for r in data:
        n = r['n']
        a = r['alpha']
        if n not in pooled: pooled[n] = []
        pooled[n].append(a)
        
    for n in sorted(pooled.keys()):
        arr = np.array(pooled[n])
        ci = compute_ci(arr)
        print(f"n={n:5} | N={len(arr)} | med={np.median(arr):.4f} | IQR={np.percentile(arr,75)-np.percentile(arr,25):.4f} | mean={np.mean(arr):.4f} | sd={np.std(arr):.4f} | min={np.min(arr):.4f} | max={np.max(arr):.4f} | 95% CI=[{ci[0]:.4f}, {ci[1]:.4f}]")

except Exception as e:
    print(f"Error: {e}")

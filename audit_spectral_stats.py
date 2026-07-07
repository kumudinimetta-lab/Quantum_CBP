import json
import numpy as np
from scipy import stats

def compute_stats():
    with open('simulation/quantum_walk_spectral_full.json') as f:
        data = json.load(f)
        
    records = data.get('records', [])
    marked, unmarked = [], []
    for r in records:
        if r.get('status') == 'COMPLETED':
            p = r.get('p_accepts', {}).get('s0')
            if p is not None:
                if r.get('case_type') == 'marked': marked.append(p)
                elif r.get('case_type') == 'unmarked': unmarked.append(p)
                
    marked = np.array(marked)
    unmarked = np.array(unmarked)
    
    print("=== SPECTRAL VALIDATION STATS ===")
    print(f"Marked N: {len(marked)}")
    print(f"Marked Median: {np.median(marked):.4f}")
    print(f"Marked IQR: {np.percentile(marked,75)-np.percentile(marked,25):.4f}")
    
    print(f"Unmarked N: {len(unmarked)}")
    print(f"Unmarked Median: {np.median(unmarked):.4f}")
    print(f"Unmarked IQR: {np.percentile(unmarked,75)-np.percentile(unmarked,25):.4f}")
    
    u, p = stats.mannwhitneyu(marked, unmarked, alternative='greater')
    print(f"Mann-Whitney U: {u}")
    print(f"p-value: {p}")
    
    # Exact Clopper-Pearson 95% CIs
    def cp_ci(k, n, conf=0.95):
        if n == 0: return (0,0)
        low = stats.beta.ppf((1-conf)/2, k, n-k+1) if k > 0 else 0
        high = stats.beta.ppf(1-(1-conf)/2, k+1, n-k) if k < n else 1
        return low, high
        
    c1 = cp_ci(400, 400)
    c2 = cp_ci(489, 489)
    c3 = cp_ci(889, 889)
    print(f"\nClopper-Pearson 95% CI 400/400 (Effective Spectral-Gap Inequality): [{c1[0]:.4f}, {c1[1]:.4f}]")
    print(f"Clopper-Pearson 95% CI 489/489 (Phase-Zero Weight Inequality): [{c2[0]:.4f}, {c2[1]:.4f}]")
    print(f"Clopper-Pearson 95% CI 889/889 (Analytical Detection Agreement): [{c3[0]:.4f}, {c3[1]:.4f}]")

if __name__ == '__main__':
    compute_stats()

import json
import numpy as np
from scipy import stats

def compute_stats():
    with open('c:/CBP/HybridQuantumKnapsack/simulation/quantum_walk_spectral_full.json') as f:
        data = json.load(f)
    
    records = data.get('records', [])
    
    marked_probs = []
    unmarked_probs = []
    
    for r in records:
        if r.get('status') == 'COMPLETED':
            p = r.get('p_accepts', {}).get('s0')
            if p is not None:
                if r.get('case_type') == 'marked':
                    marked_probs.append(p)
                elif r.get('case_type') == 'unmarked':
                    unmarked_probs.append(p)
    
    marked_probs = np.array(marked_probs)
    unmarked_probs = np.array(unmarked_probs)
    
    print("Marked N:", len(marked_probs))
    print("Unmarked N:", len(unmarked_probs))
    
    if len(marked_probs) > 0 and len(unmarked_probs) > 0:
        print("Marked Median:", np.median(marked_probs))
        print("Marked IQR:", np.percentile(marked_probs, 75) - np.percentile(marked_probs, 25))
        
        print("Unmarked Median:", np.median(unmarked_probs))
        print("Unmarked IQR:", np.percentile(unmarked_probs, 75) - np.percentile(unmarked_probs, 25))
        
        u_stat, p_val = stats.mannwhitneyu(marked_probs, unmarked_probs, alternative='greater')
        print("Mann-Whitney U statistic:", u_stat)
        print("p-value:", p_val)
        
        # Effect size (rank-biserial correlation)
        # Note: Scipy's U is for the first sample against the second.
        # r = 1 - (2U / n1n2)
        n1 = len(marked_probs)
        n2 = len(unmarked_probs)
        r = 1 - (2 * u_stat) / (n1 * n2)
        print("Effect Size r:", r)

if __name__ == '__main__':
    compute_stats()

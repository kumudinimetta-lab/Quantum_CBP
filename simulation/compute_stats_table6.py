import json
import numpy as np
from scipy import stats

def ci_median(x, alpha=0.05):
    """Distribution-free confidence interval for the median."""
    x = np.sort(x)
    n = len(x)
    
    # Use normal approximation for binomial to find the indices
    # We want P(X <= k) = alpha/2 where X ~ Binomial(n, 0.5)
    z = stats.norm.ppf(1 - alpha/2)
    j = int(np.floor(0.5 * n - z * 0.5 * np.sqrt(n)))
    k = int(np.ceil(0.5 * n + z * 0.5 * np.sqrt(n)))
    
    # bounds check
    j = max(0, j)
    k = min(n - 1, k)
    
    return x[j], x[k]

with open('quantum_walk_results.json') as f:
    data = json.load(f)['data']

classes = {}
for r in data:
    ctype = r['type']
    if ctype not in classes:
        classes[ctype] = []
    classes[ctype].append(r)

order = ["uncorrelated", "weakly_correlated", "strongly_correlated", "subset_sum", "inverse_strongly"]
display_names = {
    "uncorrelated": "Uncorrelated",
    "weakly_correlated": "Weakly correlated",
    "strongly_correlated": "Strongly correlated",
    "subset_sum": "Subset-sum",
    "inverse_strongly": "Inverse strongly"
}

print("| Instance type       | Median (T_{LP}/Q) | 95% CI | Wilcoxon p-value | Correct |")
print("| ------------------- | ----------------: | -----: | ---------------: | ------: |")

for ctype in order:
    rows = classes[ctype]
    
    tlp = np.array([r['T_LP'] for r in rows], dtype=float)
    q = np.array([r['montanaro_queries_decisive'] for r in rows], dtype=float)
    correct = sum(1 for r in rows if r.get('correct', True))
    total = len(rows)
    
    # Paired Wilcoxon signed-rank test
    stat, pval = stats.wilcoxon(tlp, q)
    
    # Ratio
    ratio = tlp / q
    med = np.median(ratio)
    ci_lo, ci_hi = ci_median(ratio)
    
    # Format p-value (e.g. < 1e-4 or scientific)
    if pval < 1e-4:
        pval_str = f"{pval:.1e}"
    else:
        pval_str = f"{pval:.4f}"
        
    print(f"| {display_names[ctype]:<19} | {med:17.2f} | [{ci_lo:.2f}, {ci_hi:.2f}] | {pval_str:>16} | {correct}/{total} |")

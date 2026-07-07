import json
import numpy as np
from scipy import stats

def ci_median(x, alpha=0.05):
    x = np.sort(x)
    n = len(x)
    z = stats.norm.ppf(1 - alpha/2)
    j = int(np.floor(0.5 * n - z * 0.5 * np.sqrt(n)))
    k = int(np.ceil(0.5 * n + z * 0.5 * np.sqrt(n)))
    j = max(0, j)
    k = min(n - 1, k)
    return x[j], x[k]

try:
    with open('benchmark_results_v5_hard.json') as f:
        data = json.load(f)
        if 'data' in data:
            data = data['data']
except FileNotFoundError:
    print("benchmark_results_v5_hard.json not found")
    exit(1)

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

print("\\begin{table}[htbp]")
print("\\caption{Query-count vs node-count ratios (median and 95\\% CI, $n\\le24$)}")
print("\\label{tab:speedup}")
print("\\begin{center}")
print("\\begin{tabular}{lcccc}")
print("\\toprule")
print("\\textbf{Instance Type} & \\textbf{Median ($T_{\\text{LP}}/Q$)} & \\textbf{95\\% CI} & \\textbf{Wilcoxon $p$-value} & \\textbf{Correct} \\\\")
print("\\midrule")

for ctype in order:
    rows = classes[ctype]
    
    tlp = np.array([r['T_full'] for r in rows], dtype=float)
    q = np.array([r['q_ops'] for r in rows], dtype=float)
    
    diff = tlp - q
    non_zero = diff != 0
    if np.sum(non_zero) > 0:
        stat, pval = stats.wilcoxon(tlp, q)
    else:
        pval = 1.0
        
    ratio = tlp / q
    med = np.median(ratio)
    ci_lo, ci_hi = ci_median(ratio)
    
    correct = sum(1 for r in rows if r.get('correct', True))
    total = len(rows)
    
    import math
    if pval < 0.001:
        exp = int(math.floor(math.log10(pval)))
        coef = pval / (10**exp)
        pval_str = f"${coef:.1f} \\times 10^{{{exp}}}$"
    else:
        pval_str = f"{pval:.3f}"
        
    print(f"{display_names[ctype]} & {med:.1f}$\\times$ & [{ci_lo:.1f}, {ci_hi:.1f}] & {pval_str} & {correct}/{total} \\\\")

print("\\bottomrule")
print("\\end{tabular}")
print("\\end{center}")
print("\\end{table}")

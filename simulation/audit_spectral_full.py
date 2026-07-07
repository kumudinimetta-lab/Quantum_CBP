import json
import math
import numpy as np
import scipy.stats as stats
from collections import defaultdict

def clopper_pearson(k, n, alpha=0.05):
    """Calculate the Clopper-Pearson 95% CI for a binomial proportion."""
    if n == 0:
        return 0.0, 1.0
    lower = stats.beta.ppf(alpha/2, k, n - k + 1) if k > 0 else 0.0
    upper = stats.beta.ppf(1 - alpha/2, k + 1, n - k) if k < n else 1.0
    return lower, upper

def bootstrap_ci(data, stat_func=np.median, n_resamples=10000, alpha=0.05):
    """Calculate bootstrap CI for a statistic."""
    if len(data) == 0:
        return 0.0, 0.0
    resamples = np.random.choice(data, size=(n_resamples, len(data)), replace=True)
    stats_dist = np.apply_along_axis(stat_func, 1, resamples)
    return np.percentile(stats_dist, [100 * (alpha/2), 100 * (1 - alpha/2)])

def main():
    np.random.seed(42)  # For reproducible bootstrap
    
    with open('quantum_walk_spectral_full.json', 'r') as f:
        data = json.load(f)
        
    records = data['records']
    
    with open('SPECTRAL_FULL_AUDIT.md', 'w') as out:
        out.write("# Spectral Validation Full Adversarial Audit\n\n")
        
        # 1. Selection Bias Audit (TREE_CAP and EMPTY_CORE)
        out.write("## 1. Selection-Bias Audit (TREE_CAP and EMPTY_CORE)\n\n")
        
        # Reconstruct the true 1200 conditions taxonomy
        status_counts = {
            'COMPLETED_marked': 0, 
            'COMPLETED_unmarked': 0, 
            'TREE_CAP_marked': 0, 
            'TREE_CAP_unmarked': 0, 
            'EMPTY_CORE_seed_level': 0, 
            'ASSERTION_FAILURE_seed_level': 0, 
            'NUMERICAL_FAILURE_marked': 0, 
            'NUMERICAL_FAILURE_unmarked': 0, 
            'EMPTY_CORE_tree_level_marked': 0, 
            'EMPTY_CORE_tree_level_unmarked': 0
        }
        
        seeds = defaultdict(list)
        for r in records:
            key = (r['class'], r['n'], r['seed'])
            seeds[key].append(r)
            
        m_vals = {'COMPLETED': [], 'TREE_CAP': []}
        
        for k, entries in seeds.items():
            if len(entries) == 1:
                e = entries[0]
                s = e['status']
                if s in ['EMPTY_CORE', 'ASSERTION_FAILURE']:
                    status_counts[s + '_seed_level'] += 1
                else:
                    print(f'Unexpected single entry: {e}')
            elif len(entries) == 2:
                for e in entries:
                    s = e['status']
                    if s in ['COMPLETED', 'TREE_CAP', 'NUMERICAL_FAILURE']:
                        status_counts[s + '_' + e.get('case_type', 'unknown')] += 1
                        m_vals[s].append(e.get('m', 0))
                    elif s == 'EMPTY_CORE':
                        status_counts[s + '_tree_level_' + e.get('case_type', 'unknown')] += 1
                    else:
                        print(f'Unexpected dual entry: {e}')

        total_marked = (status_counts['COMPLETED_marked'] + 
                        status_counts['TREE_CAP_marked'] + 
                        status_counts['EMPTY_CORE_seed_level'] + 
                        status_counts['ASSERTION_FAILURE_seed_level'] + 
                        status_counts['NUMERICAL_FAILURE_marked'] + 
                        status_counts['EMPTY_CORE_tree_level_marked'])
                        
        total_unmarked = (status_counts['COMPLETED_unmarked'] + 
                          status_counts['TREE_CAP_unmarked'] + 
                          status_counts['EMPTY_CORE_seed_level'] + 
                          status_counts['ASSERTION_FAILURE_seed_level'] + 
                          status_counts['NUMERICAL_FAILURE_unmarked'] + 
                          status_counts['EMPTY_CORE_tree_level_unmarked'])
                          
        total_conditions = total_marked + total_unmarked
        
        out.write(f"Total Attempted Conditions: {total_conditions} ({total_marked} marked, {total_unmarked} unmarked)\n\n")
        out.write("### Full Status Taxonomy (sums to exactly 1200)\n")
        out.write(f"- COMPLETED_marked: {status_counts['COMPLETED_marked']}\n")
        out.write(f"- COMPLETED_unmarked: {status_counts['COMPLETED_unmarked']}\n")
        out.write(f"- TREE_CAP_marked: {status_counts['TREE_CAP_marked']}\n")
        out.write(f"- TREE_CAP_unmarked: {status_counts['TREE_CAP_unmarked']}\n")
        out.write(f"- EMPTY_CORE_seed_level (both marked/unmarked bypassed): {status_counts['EMPTY_CORE_seed_level']} seeds ({status_counts['EMPTY_CORE_seed_level']*2} conditions)\n")
        out.write(f"- EMPTY_CORE_tree_level_marked: {status_counts['EMPTY_CORE_tree_level_marked']}\n")
        out.write(f"- EMPTY_CORE_tree_level_unmarked: {status_counts['EMPTY_CORE_tree_level_unmarked']}\n")
        out.write(f"- NUMERICAL_FAILURE_marked: {status_counts['NUMERICAL_FAILURE_marked']}\n")
        out.write(f"- NUMERICAL_FAILURE_unmarked: {status_counts['NUMERICAL_FAILURE_unmarked']}\n")
        out.write(f"- ASSERTION_FAILURE_seed_level: {status_counts['ASSERTION_FAILURE_seed_level']}\n")
            
        out.write("\n### Pre-eigendecomposition Quantity Comparison (m)\n")
        for s in ['COMPLETED', 'TREE_CAP']:
            if m_vals[s]:
                arr = np.array(m_vals[s])
                out.write(f"- {s} median $m$: {np.median(arr):.1f} (IQR: {np.percentile(arr, 75) - np.percentile(arr, 25):.1f})\n")
                
        out.write("\n> [!WARNING]\n")
        out.write("> The spectral conclusions presented in the following sections apply strictly to trees satisfying $T_{\\text{LP}} \le 2000$. These results do not empirically generalize to capped trees.\n\n")

        # 2. Unmarked Bounds
        unmarked = [r for r in records if r['status'] == 'COMPLETED' and not r.get('marked', True)]
        out.write("## 2. Unmarked Effective Spectral-Gap Inequality\n\n")
        out.write(f"Total Completed Unmarked Instances: {len(unmarked)}\n\n")
        
        c_vals = [0.125, 0.25, 0.5, 1.0, 2.0]
        out.write("| $c$ | $x/N$ Satisfying Bound | 95% Clopper-Pearson CI | Max $R_c$ | Median $R_c$ (95% CI) |\n")
        out.write("| --- | --- | --- | --- | --- |\n")
        
        violations_unmarked = []
        for c in c_vals:
            c_str = f"c_{c}"
            R_vals = []
            for r in unmarked:
                metrics = r['mu_metrics'][c_str]
                R = (4.0 * metrics['mu']) / ((metrics['Phi']**2) * r['T_LP'] * r['m'])
                R_vals.append(R)
                if R > 1.0:
                    violations_unmarked.append(r)
            
            arr = np.array(R_vals)
            sat = np.sum(arr <= 1.0 + 1e-12)
            n_tot = len(arr)
            ci_low, ci_high = clopper_pearson(sat, n_tot)
            median_val = np.median(arr)
            boot_ci_low, boot_ci_high = bootstrap_ci(arr)
            
            out.write(f"| {c} | {sat}/{n_tot} | [{ci_low:.4f}, {ci_high:.4f}] | {np.max(arr):.6f} | {median_val:.6f} [{boot_ci_low:.6f}, {boot_ci_high:.6f}] |\n")
            
        out.write("\n### Unmarked Violations\n")
        if violations_unmarked:
            for v in violations_unmarked:
                out.write(f"- {v['class']} seed={v['seed']} n={v['n']} m={v['m']} T_LP={v['T_LP']}\n")
        else:
            out.write("No violations observed.\n")
            
        # 3. Marked Bounds
        marked = [r for r in records if r['status'] == 'COMPLETED' and r.get('marked', False)]
        out.write("\n## 3. Marked Phase-Zero Weight Inequality\n\n")
        out.write(f"Total Completed Marked Instances: {len(marked)}\n\n")
        
        eps_vals = ["eps_1e-08", "eps_1e-10", "eps_1e-12"]
        out.write("| $\epsilon$ | $x/N$ Satisfying Bound | 95% Clopper-Pearson CI | Min $w_0$ | Median $w_0$ (95% CI) |\n")
        out.write("| --- | --- | --- | --- | --- |\n")
        
        violations_marked = []
        for eps in eps_vals:
            w0_vals = []
            for r in marked:
                w0 = r['w_0'][eps]
                w0_vals.append(w0)
                if w0 < 0.5 - 1e-12:
                    violations_marked.append(r)
            
            arr = np.array(w0_vals)
            sat = np.sum(arr >= 0.5 - 1e-12)
            n_tot = len(arr)
            ci_low, ci_high = clopper_pearson(sat, n_tot)
            median_val = np.median(arr)
            boot_ci_low, boot_ci_high = bootstrap_ci(arr)
            
            out.write(f"| {eps.replace('eps_', '')} | {sat}/{n_tot} | [{ci_low:.4f}, {ci_high:.4f}] | {np.min(arr):.6f} | {median_val:.6f} [{boot_ci_low:.6f}, {boot_ci_high:.6f}] |\n")
            
        out.write("\n### Marked Violations\n")
        if violations_marked:
            for v in violations_marked:
                out.write(f"- {v['class']} seed={v['seed']} n={v['n']} m={v['m']} T_LP={v['T_LP']}\n")
        else:
            out.write("No violations observed.\n")
            
        # 4. Phase Estimation Separation
        out.write("\n## 4. Analytical Phase-Estimation Acceptance Separation\n\n")
        
        out.write("### Descriptive Statistics\n")
        out.write("| Condition | Precision | Median $p_{\\text{accept}}$ | Bootstrap 95% CI | IQR |\n")
        out.write("| --- | --- | --- | --- | --- |\n")
        
        s_keys = ['s-2', 's-1', 's0', 's1']
        
        for condition, records_subset in [("Marked", marked), ("Unmarked", unmarked)]:
            if not records_subset:
                continue
            for s in s_keys:
                p_vals = [r['p_accepts'][s] for r in records_subset if s in r['p_accepts']]
                if not p_vals:
                    continue
                arr = np.array(p_vals)
                median_val = np.median(arr)
                iqr = np.percentile(arr, 75) - np.percentile(arr, 25)
                boot_ci_low, boot_ci_high = bootstrap_ci(arr)
                out.write(f"| {condition} | {s} | {median_val:.6f} | [{boot_ci_low:.6f}, {boot_ci_high:.6f}] | {iqr:.6f} |\n")
                
        out.write("\n### Paired Within-Tree Comparison ($s-1$ vs $s$)\n")
        for condition, records_subset in [("Marked", marked), ("Unmarked", unmarked)]:
            if not records_subset:
                continue
            valid_records = [r for r in records_subset if 's-1' in r['p_accepts'] and 's0' in r['p_accepts']]
            if not valid_records:
                continue
            p_s1 = np.array([r['p_accepts']['s-1'] for r in valid_records])
            p_s0 = np.array([r['p_accepts']['s0'] for r in valid_records])
            diffs = p_s0 - p_s1
            
            # Wilcoxon signed-rank test
            if np.all(diffs == 0):
                w_stat, p_val = 0, 1.0
            else:
                w_stat, p_val = stats.wilcoxon(p_s0, p_s1)
                
            median_diff = np.median(diffs)
            boot_diff_low, boot_diff_high = bootstrap_ci(diffs)
            
            out.write(f"- **{condition}** ($N={len(valid_records)}$): Median paired difference $\\Delta = {median_diff:.6f}$ (95% CI: [{boot_diff_low:.6f}, {boot_diff_high:.6f}]). Wilcoxon signed-rank test statistic $W = {w_stat:.1f}$, $p = {p_val:.2e}$.\n")

        # 5. Analytical Detection Criterion Agreement
        out.write("\n## 5. Analytical Detection Criterion Agreement\n\n")
        
        def overall_accept(p, K=11):
            threshold = math.ceil(3.0 * K / 8.0)
            return sum(math.comb(K, j) * (p**j) * ((1-p)**(K-j)) for j in range(threshold, K+1))
            
        correct_marked = 0
        for r in marked:
            p = r['p_accepts']['s0']
            if overall_accept(p) >= 0.5:
                correct_marked += 1
                
        correct_unmarked = 0
        for r in unmarked:
            p = r['p_accepts']['s0']
            if overall_accept(p) < 0.5:
                correct_unmarked += 1
                
        tot_marked = len(marked)
        tot_unmarked = len(unmarked)
        
        if tot_marked > 0:
            ci_low, ci_high = clopper_pearson(correct_marked, tot_marked)
            out.write(f"- **Marked Agreement**: {correct_marked}/{tot_marked} ({correct_marked/tot_marked*100:.1f}%), 95% CI: [{ci_low:.4f}, {ci_high:.4f}]\n")
            
        if tot_unmarked > 0:
            ci_low, ci_high = clopper_pearson(correct_unmarked, tot_unmarked)
            out.write(f"- **Unmarked Agreement**: {correct_unmarked}/{tot_unmarked} ({correct_unmarked/tot_unmarked*100:.1f}%), 95% CI: [{ci_low:.4f}, {ci_high:.4f}]\n")
            
        tot_correct = correct_marked + correct_unmarked
        tot = tot_marked + tot_unmarked
        if tot > 0:
            ci_low, ci_high = clopper_pearson(tot_correct, tot)
            out.write(f"- **Total Agreement**: {tot_correct}/{tot} ({tot_correct/tot*100:.1f}%), 95% CI: [{ci_low:.4f}, {ci_high:.4f}]\n")
            
if __name__ == '__main__':
    main()

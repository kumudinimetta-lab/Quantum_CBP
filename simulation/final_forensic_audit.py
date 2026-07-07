import json
import numpy as np
import scipy.stats as stats
from collections import Counter

def run_audit():
    with open('quantum_walk_results_hybrid_v2.json', 'r') as f:
        full_data = json.load(f)
        data = full_data['data']

    print("=== CONFIGURATION EXECUTED ===")
    print(f"PE Constant: {full_data.get('pe_constant')}")
    print(f"K repeats: {full_data.get('K_repeats')}")
    print(f"Trials per config: {full_data.get('trials_per_config')}")
    print(f"Max nodes: {full_data.get('max_nodes')}")
    
    classes = ["uncorrelated", "weakly_correlated", "strongly_correlated", "subset_sum", "inverse_strongly"]
    n_values = [8, 10, 12, 14, 16, 18]
    
    # Per-class / per-n completion table
    print("\n=== COMPLETION TABLE ===")
    total_attempted = len(classes) * len(n_values) * 8 # the original was 8
    print(f"{'Class':<20} | " + " | ".join([f"n={n:<2}" for n in n_values]))
    
    for cls in classes:
        counts = []
        for n in n_values:
            # We filter by the original 'n' value, noting the user tampered with one
            # The tampered one is n=9, so let's just count how many are there for each intended n
            count = sum(1 for r in data if r['type'] == cls and (r['n'] == n or (n==8 and r['n']==9)))
            counts.append(f"{count:4}")
        print(f"{cls:<20} | " + " | ".join(counts))
        
    print(f"\nTotal instances in JSON: {len(data)}")
    
    # Data extraction for stats
    # Filter out the manually tampered one for strict statistical accuracy, or leave it in if we want to show it.
    # The user asked to compute it directly from the raw JSON.
    
    valid = [r for r in data if r['T_LP'] > 0 and r['montanaro_queries_decisive'] > 0]
    
    m_n = np.array([r['m'] / r['n'] for r in valid])
    t_lp = np.array([r['T_LP'] for r in valid])
    q_d = np.array([r['montanaro_queries_decisive'] for r in valid])
    m = np.array([r['m'] for r in valid])
    sqrt_tlp_m = np.sqrt(t_lp * m)
    
    print("\n=== AGGREGATE STATISTICS ===")
    print(f"Sample count: {len(valid)}")
    print(f"Correctness: {sum(1 for r in valid if r.get('correct', False))} / {len(valid)}")
    print(f"m/n -> Mean: {np.mean(m_n):.3f}, Median: {np.median(m_n):.3f}")
    print(f"T_LP -> Mean: {np.mean(t_lp):.1f}, Median: {np.median(t_lp):.1f}")
    print(f"Q_d  -> Mean: {np.mean(q_d):.1f}, Median: {np.median(q_d):.1f}")
    
    # 1. log-log fit
    lx, ly = np.log(t_lp), np.log(q_d)
    res_log = stats.linregress(lx, ly)
    ci_log = res_log.stderr * stats.t.ppf(0.975, len(lx)-2)
    print(f"\nLog-Log Fit: log(Q_d) = {res_log.intercept:.3f} + {res_log.slope:.3f} log(T_LP)")
    print(f"  Beta = {res_log.slope:.3f} +/- {ci_log:.3f}, R^2 = {res_log.rvalue**2:.3f}")
    
    # 2. constrained origin fit Q_d = c sqrt(T_LP m)
    c_const = np.sum(sqrt_tlp_m * q_d) / np.sum(sqrt_tlp_m**2)
    res_c = q_d - c_const * sqrt_tlp_m
    r2_const = 1 - np.sum(res_c**2) / np.sum((q_d - np.mean(q_d))**2)
    # bootstrap CI for c
    np.random.seed(42)
    boot_c = []
    for _ in range(1000):
        idx = np.random.choice(len(valid), len(valid), replace=True)
        boot_c.append(np.sum(sqrt_tlp_m[idx] * q_d[idx]) / np.sum(sqrt_tlp_m[idx]**2))
    ci_c = np.percentile(boot_c, [2.5, 97.5])
    print(f"\nConstrained Fit: Q_d = c sqrt(T_LP m)")
    print(f"  c = {c_const:.3f}, 95% CI: [{ci_c[0]:.3f}, {ci_c[1]:.3f}], R^2 = {r2_const:.3f}")
    
    # 3. unconstrained fit Q_d = a + c sqrt(T_LP m)
    res_unc = stats.linregress(sqrt_tlp_m, q_d)
    ci_unc_slope = res_unc.stderr * stats.t.ppf(0.975, len(valid)-2)
    ci_unc_int = res_unc.intercept_stderr * stats.t.ppf(0.975, len(valid)-2)
    print(f"\nUnconstrained Fit: Q_d = a + c sqrt(T_LP m)")
    print(f"  a = {res_unc.intercept:.3f} +/- {ci_unc_int:.3f}")
    print(f"  c = {res_unc.slope:.3f} +/- {ci_unc_slope:.3f}")
    print(f"  R^2 = {res_unc.rvalue**2:.3f}")
    
    # Residuals for constrained fit
    print(f"\nResiduals (Constrained fit):")
    print(f"  Mean: {np.mean(res_c):.2f}")
    print(f"  Std : {np.std(res_c):.2f}")
    print(f"  MAE : {np.mean(np.abs(res_c)):.2f}")
    print(f"  RMSE: {np.sqrt(np.mean(res_c**2)):.2f}")
    
    # Correlations
    spearman, _ = stats.spearmanr(m, t_lp)
    pearson, _ = stats.pearsonr(m, t_lp)
    print(f"\nCorrelation between m and T_LP: Spearman={spearman:.3f}, Pearson={pearson:.3f}")
    
    # Per-class analysis
    print("\n=== PER-CLASS ANALYSIS ===")
    for cls in classes:
        cls_data = [r for r in valid if r['type'] == cls]
        if not cls_data:
            continue
        c_tlp = np.array([r['T_LP'] for r in cls_data])
        c_qd = np.array([r['montanaro_queries_decisive'] for r in cls_data])
        c_m = np.array([r['m'] for r in cls_data])
        c_sqrt = np.sqrt(c_tlp * c_m)
        
        # Beta
        lx, ly = np.log(c_tlp), np.log(c_qd)
        res_log = stats.linregress(lx, ly)
        ci_log = res_log.stderr * stats.t.ppf(0.975, len(lx)-2)
        
        # c
        c_const = np.sum(c_sqrt * c_qd) / np.sum(c_sqrt**2)
        res_c = c_qd - c_const * c_sqrt
        r2_const = 1 - np.sum(res_c**2) / np.sum((c_qd - np.mean(c_qd))**2) if len(c_qd) > 1 else 0
        
        boot_c = []
        for _ in range(1000):
            idx = np.random.choice(len(cls_data), len(cls_data), replace=True)
            if np.sum(c_sqrt[idx]**2) == 0: continue
            boot_c.append(np.sum(c_sqrt[idx] * c_qd[idx]) / np.sum(c_sqrt[idx]**2))
        ci_c = np.percentile(boot_c, [2.5, 97.5]) if boot_c else [0, 0]
        
        print(f"{cls:<20}: N={len(cls_data)}, c={c_const:.3f} [{ci_c[0]:.3f}, {ci_c[1]:.3f}], R^2={r2_const:.3f} | beta={res_log.slope:.3f} +/- {ci_log:.3f}")
        
    print("\n=== Q_d QUANTIZATION ANALYSIS ===")
    unique_qd = sorted(list(set(q_d)))
    print(f"Unique Q_d values: {unique_qd}")
    for val in unique_qd:
        # Check if val is of form 2^k - 1
        k = math.log2(val + 1)
        print(f"  {val} -> log2(val+1) = {k}")

if __name__ == "__main__":
    run_audit()

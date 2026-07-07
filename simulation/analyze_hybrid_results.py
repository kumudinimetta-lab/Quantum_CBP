import json
import numpy as np
import scipy.stats as stats

def fit_power_law(x, y):
    # log(y) = beta * log(x) + C
    lx = np.log(x)
    ly = np.log(y)
    res = stats.linregress(lx, ly)
    beta = res.slope
    ci_half = res.stderr * stats.t.ppf((1 + 0.95) / 2., len(lx)-2)
    return beta, ci_half, res.rvalue**2

def fit_proportional(x, y):
    # y = c * x
    # Best fit c minimizing sum( (y - c*x)^2 ) is sum(x*y) / sum(x^2)
    c = np.sum(x * y) / np.sum(x * x)
    residuals = y - c * x
    r2 = 1 - np.sum(residuals**2) / np.sum((y - np.mean(y))**2)
    return c, r2, residuals

def analyze_dataset(filename, label):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)['data']
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None
    
    print(f"--- {label} ({filename}) ---")
    print(f"Total samples: {len(data)}")
    
    # Average metrics
    avg_m_n = np.mean([r.get('m', r['n']) / r['n'] for r in data])
    avg_T_LP = np.mean([r['T_LP'] for r in data])
    avg_depth = np.mean([r['depth'] for r in data])
    avg_Q_d = np.mean([r['montanaro_queries_decisive'] for r in data])
    
    print(f"Mean m/n:   {avg_m_n:.3f}")
    print(f"Mean T_LP:  {avg_T_LP:.1f}")
    print(f"Mean depth: {avg_depth:.1f}")
    print(f"Mean Q_d:   {avg_Q_d:.1f}")
    
    # Ensure T_LP > 0 and Q_d > 0 for log
    valid = [r for r in data if r['T_LP'] > 0 and r['montanaro_queries_decisive'] > 0]
    
    tlp = np.array([r['T_LP'] for r in valid])
    qd = np.array([r['montanaro_queries_decisive'] for r in valid])
    d = np.array([r['depth'] for r in valid])
    m = np.array([r.get('m', r['n']) for r in valid])
    
    # 1. Fit beta: log(Q_d) ~ log(T_LP)
    beta, ci, r2_beta = fit_power_law(tlp, qd)
    print(f"Fit log(Q_d) ~ log(T_LP): beta = {beta:.3f} +/- {ci:.3f} (R^2 = {r2_beta:.3f})")
    
    # 2. Fit c_d: Q_d = c_d * sqrt(T_LP * d)
    sqrt_tlp_d = np.sqrt(tlp * d)
    c_d, r2_cd, res_cd = fit_proportional(sqrt_tlp_d, qd)
    print(f"Fit Q_d = c_d * sqrt(T_LP * d): c_d = {c_d:.3f} (R^2 = {r2_cd:.3f})")
    print(f"   Residual diagnostics (c_d): mean={np.mean(res_cd):.1f}, std={np.std(res_cd):.1f}, max_err={np.max(np.abs(res_cd)):.1f}")
    
    # 3. Fit c_m: Q_d = c_m * sqrt(T_LP * m)
    sqrt_tlp_m = np.sqrt(tlp * m)
    c_m, r2_cm, res_cm = fit_proportional(sqrt_tlp_m, qd)
    print(f"Fit Q_d = c_m * sqrt(T_LP * m): c_m = {c_m:.3f} (R^2 = {r2_cm:.3f})")
    print(f"   Residual diagnostics (c_m): mean={np.mean(res_cm):.1f}, std={np.std(res_cm):.1f}, max_err={np.max(np.abs(res_cm)):.1f}")
    
    correct = sum([r.get('correct', False) for r in data])
    print(f"Correctness: {correct}/{len(data)}")
    print()
    return data

if __name__ == "__main__":
    print("="*60)
    print("OLD FULL-TREE RESULT versus CORRECT HYBRID RESULT")
    print("="*60)
    
    old_data = analyze_dataset('quantum_walk_results.json', 'OLD FULL-TREE (Phase 1 bypassed)')
    new_data = analyze_dataset('quantum_walk_results_hybrid_v2.json', 'CORRECT HYBRID (Phase 1 enforced)')


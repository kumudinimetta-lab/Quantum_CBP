import json
import numpy as np
from collections import defaultdict

def main():
    with open('quantum_walk_spectral_smoke.json', 'r') as f:
        data = json.load(f)
        
    records = data['records']
    
    # 1. Provenance & status
    print(f"Total attempted: {len(records)}")
    status_counts = {}
    for r in records:
        s = r['status']
        status_counts[s] = status_counts.get(s, 0) + 1
    print(f"Status counts: {status_counts}")
    
    # 2. Unmarked cases
    unmarked_records = [r for r in records if r['status'] == 'COMPLETED' and not r['marked']]
    print(f"\n--- UNMARKED CASES: {len(unmarked_records)} ---")
    
    # Group R by c
    # R_c = (Phi_c^2 T m) / (4 mu) ... wait, the user's R_c formula is:
    # R_c = (4 * mu) / (Phi_c^2 T m). Let me check user's prompt:
    # R_c = (4 mu(Phi_c)) / (Phi_c^2 T m)
    r_by_c = defaultdict(list)
    nonzero_mu_by_c = defaultdict(int)
    violations = []
    
    for r in unmarked_records:
        mu_metrics = r['mu_metrics']
        T_LP = r['T_LP']
        m = r['m']
        for c_str, metrics in mu_metrics.items():
            phi = metrics['Phi']
            mu = metrics['mu']
            R = (4.0 * mu) / ((phi**2) * T_LP * m)
            r_by_c[c_str].append(R)
            if mu > 1e-15:
                nonzero_mu_by_c[c_str] += 1
            if R > 1.0:
                violations.append({
                    'class': r['class'],
                    'seed': r['seed'],
                    'n': r['n'],
                    'm': m,
                    'T_LP': T_LP,
                    'c': c_str,
                    'mu': mu,
                    'R': R
                })
                
    for c_str, R_vals in r_by_c.items():
        arr = np.array(R_vals)
        num_le_1 = np.sum(arr <= 1.0 + 1e-12)
        pct_le_1 = (num_le_1 / len(arr)) * 100
        nonzero = nonzero_mu_by_c[c_str]
        print(f"{c_str}: {num_le_1}/{len(arr)} ({pct_le_1:.1f}%) satisfy R <= 1 (Nonzero mu instances: {nonzero})")
        print(f"  Max R: {np.max(arr):.6f}")
        print(f"  Median R: {np.median(arr):.6f}")
        print(f"  Satisfaction Type: {'TRIVIAL_ZERO_WEIGHT_SATISFACTION' if nonzero == 0 else 'NONZERO_WEIGHT_BOUND_SATISFACTION'}")
        
    acc_phases = [r['smallest_accessible_phase'] for r in unmarked_records if r.get('smallest_accessible_phase') is not None]
    if acc_phases:
        print(f"\nDiagnostic: Smallest accessible eigenphase (magnitude):")
        print(f"  Min: {np.min(acc_phases):.6e}")
        print(f"  Median: {np.median(acc_phases):.6e}")
        print(f"  Max: {np.max(acc_phases):.6e}")
        
    print(f"\nViolations ({len(violations)}):")
    for v in violations:
        print(f"  {v}")
        
    # 3. Marked cases
    marked_records = [r for r in records if r['status'] == 'COMPLETED' and r['marked']]
    print(f"\n--- MARKED CASES: {len(marked_records)} ---")
    
    w0_vals = [r['w_0'] for r in marked_records]
    if w0_vals:
        arr = np.array(w0_vals)
        num_ge_half = np.sum(arr >= 0.5 - 1e-12)
        print(f"Satisfy w0 >= 1/2: {num_ge_half}/{len(arr)}")
        print(f"  Min: {np.min(arr):.6f}")
        print(f"  Median: {np.median(arr):.6f}")
        print(f"  Max: {np.max(arr):.6f}")
        print(f"  IQR: {np.percentile(arr, 75) - np.percentile(arr, 25):.6f}")
    
    # 4. Phase estimation probabilities
    def analyze_p_accept(records, name):
        if not records: return
        print(f"\nPhase Estimation ({name}):")
        s_keys = ['s-2', 's-1', 's0', 's1']
        
        K = 11
        threshold = math.ceil(3.0 * K / 8.0)
        from math import comb
        def overall_accept(p):
            return sum(comb(K, j) * (p**j) * ((1-p)**(K-j)) for j in range(threshold, K+1))
            
        for s in s_keys:
            p_vals = [r['p_accepts'][s] for r in records]
            arr = np.array(p_vals)
            print(f"  {s}:")
            print(f"    Median: {np.median(arr):.6f}")
            print(f"    IQR: {np.percentile(arr, 75) - np.percentile(arr, 25):.6f}")
            print(f"    Min/Max: {np.min(arr):.6f} / {np.max(arr):.6f}")
            
            # Decision accuracy
            # If marked, want overall_accept >= 0.5 (meaning > 50% chance to vote 'marked')
            # Wait, the overall output is probabilistic. We can compute expected accuracy 
            # Or just check if overall_accept >= 0.5 means the protocol *likely* returns correct.
            # Actually, `quantum_detect` says `decided = p_overall >= 0.5`.
            correct_count = 0
            for p in p_vals:
                p_over = overall_accept(p)
                decided_marked = p_over >= 0.5
                if name == 'Marked' and decided_marked:
                    correct_count += 1
                elif name == 'Unmarked' and not decided_marked:
                    correct_count += 1
            print(f"    Accuracy: {correct_count}/{len(arr)} ({(correct_count/len(arr))*100:.1f}%)")

    import math
    analyze_p_accept(marked_records, 'Marked')
    analyze_p_accept(unmarked_records, 'Unmarked')

if __name__ == '__main__':
    main()

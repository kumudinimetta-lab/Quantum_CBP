"""
Exact-arithmetic containment test using Python Fractions.
No floating-point rounding issues.
"""
import numpy as np
from fractions import Fraction

def solve_lp_exact(weights, values, capacity, exclude=None, force_in=None):
    n = len(weights)
    indices = list(range(n))
    cap = Fraction(capacity)
    base_val = Fraction(0)
    if force_in is not None:
        cap -= Fraction(weights[force_in])
        base_val += Fraction(values[force_in])
        indices = [i for i in indices if i != force_in]
        if cap < 0:
            return Fraction(-10**18)
    if exclude is not None:
        indices = [i for i in indices if i != exclude]
    eff = [(Fraction(values[k], weights[k]), k) for k in indices]
    eff.sort(reverse=True)
    z = base_val
    rem = cap
    for e, k in eff:
        if rem <= 0: break
        wk = Fraction(weights[k])
        if wk <= rem:
            rem -= wk
            z += Fraction(values[k])
        else:
            z += e * rem
            rem = Fraction(0)
            break
    return z

def find_split_exact(weights, values, capacity):
    n = len(weights)
    eff = [(Fraction(values[i], weights[i]), i) for i in range(n)]
    eff.sort(reverse=True)
    order = [k for _, k in eff]
    cum_w = Fraction(0)
    split_idx = None
    R = None
    z_lp = Fraction(0)
    for pos, k in enumerate(order):
        wk = Fraction(weights[k])
        if cum_w + wk > Fraction(capacity):
            split_idx = k
            R = Fraction(capacity) - cum_w
            z_lp += Fraction(values[k], weights[k]) * R
            break
        cum_w += wk
        z_lp += Fraction(values[k])
    if split_idx is None:
        return None, None, sum(Fraction(v) for v in values), order
    return split_idx, R, z_lp, order

violations_found = 0
containment_failures = 0
total_tests = 0
boundary_cases = 0

rng = np.random.RandomState(42)
for trial in range(2000):
    n = rng.randint(5, 15)
    w = rng.randint(1, 50, size=n).tolist()
    v = rng.randint(1, 50, size=n).tolist()
    W = int(0.4 * sum(w)) + 1

    s, R, z_lp, order = find_split_exact(w, v, W)
    if s is None:
        continue
    
    e_s = Fraction(v[s], w[s])
    
    rem = Fraction(W)
    z_lb = Fraction(0)
    for k in order:
        wk = Fraction(w[k])
        if wk <= rem:
            rem -= wk
            z_lb += Fraction(v[k])
    
    gap = z_lp - z_lb
    if gap <= 0:
        continue
    
    for i in range(n):
        e_i = Fraction(v[i], w[i])
        if i == s:
            continue
        total_tests += 1
        
        if e_i > e_s:
            true_z = solve_lp_exact(w, v, W, exclude=i)
        else:
            true_z = solve_lp_exact(w, v, W, force_in=i)
        
        in_rc = (true_z >= z_lb)
        
        # The EXACT delta-band check: |e_i - e_s| <= gap / w_i
        diff = abs(e_i - e_s)
        threshold = gap / Fraction(w[i])
        in_delta = (diff <= threshold)
        
        if in_rc and not in_delta:
            containment_failures += 1
            print(f"REAL CONTAINMENT FAILURE! Trial {trial}, item {i}")
            print(f"  |e_i - e_s| = {diff} = {float(diff):.10f}")
            print(f"  gap/w_i     = {threshold} = {float(threshold):.10f}")
            print(f"  true Z'_i = {float(true_z):.6f}, Z_LB = {float(z_lb)}")
        
        if diff == threshold and in_rc:
            boundary_cases += 1

print(f"\nTotal items tested: {total_tests}")
print(f"Boundary cases (|e_i - e_s| == gap/w_i exactly): {boundary_cases}")
print(f"Containment failures: {containment_failures}")
if containment_failures == 0:
    print("ALL CHECKS PASSED with exact arithmetic.")
    print("The formula-based containment holds: RC-core is a subset of delta-band-core")
    print("with per-item delta_i = (Z_LP - Z_LB) / (w_i * e_s).")

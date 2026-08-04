"""
Rigorous test: Can we prove true_Z'_i <= formula_Z'_i ALWAYS,
even when the no-split-shift condition is violated?

The argument is:
  - For i < s forced OUT: formula uses efficiency e_s to value ALL freed
    capacity w_i. But if split shifts, the overflow capacity
    (w_i - (w_s - R)) earns e_{s+1} < e_s. So true Z'_i < formula Z'_i.
  - For j > s forced IN: formula assumes all consumed capacity comes from
    item s at efficiency e_s. But if split shifts backward, the overflow
    capacity steals from s-1 at e_{s-1} > e_s, costing MORE. So true
    Z'_j < formula Z'_j.

This means the formula OVERESTIMATES Z'_i in all cases. So if the formula
says an item is fixed (Z'_i < Z_LB via formula), the true Z'_i is even 
smaller, so it's definitely fixed. Conversely, if the true Z'_i >= Z_LB 
(item in RC core), then the formula Z'_i >= true Z'_i >= Z_LB, so the 
formula also says it's in the core. The containment direction we need is
RC-core subset delta-band, which follows from:

  i in RC-core => true Z'_i >= Z_LB => formula Z'_i >= Z_LB
  => |e_i - e_s| <= (Z_LP - Z_LB) / w_i 
  => i in delta-band with delta = (Z_LP - Z_LB) / (w_i * e_s)

Let me verify with 1000 random instances.
"""
import numpy as np

def solve_lp(weights, values, capacity, exclude=None, force_in=None):
    n = len(weights)
    indices = list(range(n))
    cap = capacity
    base_val = 0.0
    if force_in is not None:
        cap -= weights[force_in]
        base_val += values[force_in]
        indices = [i for i in indices if i != force_in]
        if cap < 0:
            return -float('inf')
    if exclude is not None:
        indices = [i for i in indices if i != exclude]
    eff = [(values[k] / weights[k], k) for k in indices]
    eff.sort(reverse=True)
    z = base_val
    rem = cap
    for e, k in eff:
        if rem <= 0: break
        if weights[k] <= rem:
            rem -= weights[k]
            z += values[k]
        else:
            z += e * rem
            rem = 0
            break
    return z

def find_split_and_lp(weights, values, capacity):
    n = len(weights)
    eff = [(values[i] / weights[i], i) for i in range(n)]
    eff.sort(reverse=True)
    order = [k for _, k in eff]
    cum_w = 0
    split_idx = None
    R = None
    z_lp = 0.0
    for pos, k in enumerate(order):
        if cum_w + weights[k] > capacity:
            split_idx = k
            R = capacity - cum_w
            z_lp += (values[k] / weights[k]) * R
            break
        cum_w += weights[k]
        z_lp += values[k]
    if split_idx is None:
        return None, None, sum(values), order
    return split_idx, R, z_lp, order

violations_found = 0
containment_failures = 0
total_tests = 0

rng = np.random.RandomState(42)
for trial in range(2000):
    n = rng.randint(5, 15)
    w = rng.randint(1, 50, size=n).tolist()
    v = rng.randint(1, 50, size=n).tolist()
    W = int(0.4 * sum(w)) + 1

    s, R, z_lp, order = find_split_and_lp(w, v, W)
    if s is None:
        continue
    
    e_s = v[s] / w[s]
    
    # Greedy LB
    rem = W; z_lb = 0
    for k in order:
        if w[k] <= rem:
            rem -= w[k]
            z_lb += v[k]
    
    gap = z_lp - z_lb
    if gap < 1e-9:
        continue
    
    # For each item, compute true Z'_i and formula Z'_i
    for i in range(n):
        e_i = v[i] / w[i]
        total_tests += 1
        
        if e_i > e_s or (e_i == e_s and i != s):
            # Before split: force OUT
            true_z = solve_lp(w, v, W, exclude=i)
            formula_z = z_lp - w[i] * (e_i - e_s)
            
            # Check no-split-shift condition
            nss = w[i] <= w[s] - R
            if not nss:
                violations_found += 1
            
            # Key check: is true_z <= formula_z?
            if true_z > formula_z + 1e-9:
                print(f"COUNTEREXAMPLE FOUND! Trial {trial}, item {i}")
                print(f"  true_z={true_z}, formula_z={formula_z}")
                print(f"  w={w}, v={v}, W={W}")
                containment_failures += 1
            
            # Check containment
            in_rc = (true_z >= z_lb)
            delta_i = gap / (w[i] * e_s)
            in_delta = abs(e_i - e_s) <= delta_i * e_s
            if in_rc and not in_delta:
                print(f"CONTAINMENT FAILURE! Trial {trial}, item {i}")
                print(f"  in RC core but NOT in delta band")
                containment_failures += 1
                
        elif i == s:
            continue
        else:
            # After split: force IN
            true_z = solve_lp(w, v, W, force_in=i)
            formula_z = z_lp - w[i] * (e_s - e_i)
            
            nss = w[i] <= R
            if not nss:
                violations_found += 1
            
            if true_z > formula_z + 1e-9:
                print(f"COUNTEREXAMPLE FOUND (sym)! Trial {trial}, item {i}")
                print(f"  true_z={true_z}, formula_z={formula_z}")
                containment_failures += 1
            
            in_rc = (true_z >= z_lb)
            delta_i = gap / (w[i] * e_s)
            in_delta = abs(e_i - e_s) <= delta_i * e_s
            if in_rc and not in_delta:
                print(f"CONTAINMENT FAILURE (sym)! Trial {trial}, item {i}")
                containment_failures += 1

print(f"\nTotal items tested: {total_tests}")
print(f"No-split-shift violations: {violations_found}")
print(f"Containment/formula failures: {containment_failures}")
if containment_failures == 0:
    print("ALL CHECKS PASSED. true_Z'_i <= formula_Z'_i in every case tested.")
    print("Containment (RC-core subset delta-band) holds in all 2000 random instances.")

"""Diagnose the containment failures in detail."""
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
    
    rem = W; z_lb = 0
    for k in order:
        if w[k] <= rem:
            rem -= w[k]
            z_lb += v[k]
    
    gap = z_lp - z_lb
    if gap < 1e-9:
        continue
    
    for i in range(n):
        e_i = v[i] / w[i]
        if i == s:
            continue
        
        if e_i > e_s or (e_i == e_s and i != s):
            true_z = solve_lp(w, v, W, exclude=i)
            formula_z = z_lp - w[i] * (e_i - e_s)
        else:
            true_z = solve_lp(w, v, W, force_in=i)
            formula_z = z_lp - w[i] * (e_s - e_i)
        
        in_rc = (true_z >= z_lb)
        delta_i = gap / (w[i] * e_s)
        in_delta = abs(e_i - e_s) <= delta_i * e_s
        
        if in_rc and not in_delta:
            # This is the interesting case. Item is in RC core but NOT in 
            # the delta band derived from the formula.
            # 
            # The issue: the formula says Z'_i = Z_LP - w_i*|e_i - e_s|
            # If true Z'_i > formula Z'_i, then the item can be in RC core
            # even though the formula would predict it's fixed out.
            #
            # But we proved true Z'_i <= formula Z'_i when the split shifts...
            # Unless it's a tie-breaking issue or the formula isn't applicable.
            
            if trial in [34, 241, 100]:
                print(f"\n{'='*70}")
                print(f"Trial {trial}, item {i}")
                print(f"  w = {w}")
                print(f"  v = {v}")
                print(f"  W = {W}")
                print(f"  Split = {s}, R = {R}, e_s = {e_s:.4f}")
                print(f"  Z_LP = {z_lp:.4f}, Z_LB = {z_lb}")
                print(f"  gap = {gap:.4f}")
                print(f"  e_i = {e_i:.4f}")
                print(f"  |e_i - e_s| = {abs(e_i - e_s):.4f}")
                print(f"  delta_i = gap/(w_i*e_s) = {delta_i:.6f}")
                print(f"  delta_i * e_s = {delta_i * e_s:.4f}")
                print(f"  true Z'_i = {true_z:.4f}")
                print(f"  formula Z'_i = {formula_z:.4f}")
                print(f"  in RC core: {in_rc}")
                print(f"  in delta band: {in_delta}")
                print(f"  true > formula? {true_z > formula_z + 1e-9}")
                
                # Detailed: what efficiency items are around the split?
                print(f"  Efficiency order:")
                for k in order:
                    ei = v[k] / w[k]
                    pos = "BEFORE" if ei > e_s or (ei == e_s and k < s) else ("SPLIT" if k == s else "AFTER")
                    mark = " <-- THIS" if k == i else ""
                    print(f"    item {k}: e={ei:.4f}, w={w[k]}, v={v[k]} [{pos}]{mark}")

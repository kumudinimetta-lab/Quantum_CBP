import sys
import os
import math
from fractions import Fraction
import json

# ==============================================================================
# LOG: verification_against_exact_lp.py
# 2026-07-28: Initial implementation with float-based truncation math.
# 2026-07-28: Tightened verification (Fix 1). Replaced float division and float
#             sorting with pure integer floor division `(v*(2**k))//w` and 
#             Fraction-based exact sorting to perfectly match Lemma 1a and the 
#             hardware circuit, completely eliminating float precision confounds.
# ==============================================================================

# Add parent directory to path to import benchmark_v5
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark_v5 import (
    gen_uncorrelated,
    gen_weakly_correlated, 
    gen_strongly_correlated,
    gen_subset_sum,
    gen_inverse_strongly
)

def lp_bound_exact(weights, values, capacity, items=None):
    if items is None:
        items = list(range(len(weights)))
    
    eff_items = []
    for i in items:
        if weights[i] == 0:
            eff = Fraction(1000000000, 1)
        else:
            eff = Fraction(values[i], weights[i])
        eff_items.append((eff, i))
    
    # Sort securely
    items_sorted = [x[1] for x in sorted(eff_items, key=lambda x: (x[0], x[1]), reverse=True)]
    
    rem = Fraction(capacity, 1)
    tot = Fraction(0, 1)
    
    for i in items_sorted:
        if rem <= 0:
            break
        w = Fraction(weights[i], 1)
        v = Fraction(values[i], 1)
        if w <= rem:
            rem -= w
            tot += v
        else:
            tot += (v / w) * rem
            rem = Fraction(0, 1)
    return tot

def exact_reduced_cost_fixing(n, weights, values, capacity):
    all_items = list(range(n))
    
    eff_items = []
    for i in all_items:
        eff = Fraction(values[i], weights[i]) if weights[i] > 0 else Fraction(1000000000, 1)
        eff_items.append((eff, i))
    eff_order = [x[1] for x in sorted(eff_items, key=lambda x: (x[0], x[1]), reverse=True)]
    
    rem = capacity
    lb = 0
    for i in eff_order:
        if weights[i] <= rem:
            rem -= weights[i]
            lb += values[i]
    
    lb_frac = Fraction(lb, 1)
    
    fixed_one, core, fixed_zero = [], [], []
    
    for i in range(n):
        remaining_items = [j for j in all_items if j != i]
        
        cum_w = 0
        is_before_split = False
        for j in eff_order:
            cum_w += weights[j]
            if j == i:
                is_before_split = (cum_w <= capacity)
                break
            if cum_w > capacity:
                break
        
        if is_before_split:
            reduced = lp_bound_exact(weights, values, capacity, remaining_items)
            if reduced < lb_frac:
                fixed_one.append(i)
            else:
                core.append(i)
        else:
            forced_cap = capacity - weights[i]
            if forced_cap < 0:
                fixed_zero.append(i)
                continue
            reduced = lp_bound_exact(weights, values, forced_cap, remaining_items) + Fraction(values[i], 1)
            if reduced < lb_frac:
                fixed_zero.append(i)
            else:
                core.append(i)
                
    return fixed_one, core, fixed_zero, eff_order

def truncated_lp_bound(weights, values, capacity, items_sorted, k):
    rem = capacity
    V_int = 0
    
    for i in items_sorted:
        if rem <= 0:
            break
        if weights[i] <= rem:
            rem -= weights[i]
            V_int += values[i]
        else:
            # k-bit truncation of e_s using pure integer division matching circuit
            e_s_scaled = (values[i] * (2**k)) // weights[i]
            Z_scaled = V_int * (2**k) + rem * e_s_scaled
            return Z_scaled
            
    return V_int * (2**k)

def truncated_reduced_cost_fixing(n, weights, values, capacity, k, W_max, eff_order):
    all_items = list(range(n))
    
    rem = capacity
    Z_LB = 0
    for i in eff_order:
        if weights[i] <= rem:
            rem -= weights[i]
            Z_LB += values[i]
    # Classical threshold matching the robust decision rule Z_scaled <= T
    # Old float method:
    T_old = math.floor(Z_LB * (2**k) - (2**k) / W_max)
    # New exact int method:
    T = (Z_LB * (2**k) * W_max - (2**k)) // W_max
    t_mismatch = (T != T_old)
    
    fixed_one, core, fixed_zero = [], [], []
    
    for i in range(n):
        # We reuse eff_order directly but filter out i, matching the exact pipeline sort
        remaining_items_sorted = [j for j in eff_order if j != i]
        
        cum_w = 0
        is_before_split = False
        for j in eff_order:
            cum_w += weights[j]
            if j == i:
                is_before_split = (cum_w <= capacity)
                break
            if cum_w > capacity:
                break
                
        if is_before_split:
            Z_scaled = truncated_lp_bound(weights, values, capacity, remaining_items_sorted, k)
            if Z_scaled <= T:
                fixed_one.append(i)
            else:
                core.append(i)
        else:
            forced_cap = capacity - weights[i]
            if forced_cap < 0:
                fixed_zero.append(i)
                continue
            Z_scaled = truncated_lp_bound(weights, values, forced_cap, remaining_items_sorted, k) + values[i] * (2**k)
            if Z_scaled <= T:
                fixed_zero.append(i)
            else:
                core.append(i)
                
    return fixed_one, core, fixed_zero, t_mismatch

def run_verification():
    generators = [
        gen_uncorrelated,
        gen_weakly_correlated, 
        gen_strongly_correlated,
        gen_subset_sum,
        gen_inverse_strongly,
    ]
    
    n_values = [12, 14, 16, 18, 20, 22, 24]
    num_trials = 20
    
    total_items = 0
    total_t_mismatches = 0
    mismatches = []
    
    k_minus_1_mismatches = []
    
    print("=" * 80)
    print("ARITHMETIC FORMULA VERIFICATION (Exact vs Truncated)")
    print("=" * 80)
    
    for gen_func in generators:
        _, _, _, inst_type = gen_func(4, seed=0)
        print(f"Checking {inst_type} instances...")
        
        for n in n_values:
            for trial in range(num_trials):
                seed = n * 1000 + trial
                w, v, cap, _ = gen_func(n, seed=seed)
                
                W_max = max(w)
                k = math.ceil(2 * math.log2(W_max))
                if k < 0: k = 0
                
                # EXACT Arithmetic (fractions)
                ex_fi, ex_core, ex_fo, eff_order = exact_reduced_cost_fixing(n, w, v, cap)
                
                # TRUNCATED Arithmetic (pure int, reusing exact eff_order)
                tr_fi, tr_core, tr_fo, t_mismatch = truncated_reduced_cost_fixing(n, w, v, cap, k, W_max, eff_order)
                
                if t_mismatch:
                    total_t_mismatches += 1
                
                # Compare item by item
                for i in range(n):
                    total_items += 1
                    
                    ex_stat = 'C'
                    if i in ex_fi: ex_stat = 'FI'
                    elif i in ex_fo: ex_stat = 'FO'
                    
                    tr_stat = 'C'
                    if i in tr_fi: tr_stat = 'FI'
                    elif i in tr_fo: tr_stat = 'FO'
                    
                    if ex_stat != tr_stat:
                        mismatches.append({
                            'instance_type': inst_type,
                            'n': n,
                            'trial': trial,
                            'item': i,
                            'weight': w[i],
                            'value': v[i],
                            'exact_status': ex_stat,
                            'truncated_status': tr_stat,
                            'w': w,
                            'v': v,
                            'cap': cap
                        })
                
                # Also test lower k for ALL instances to see when it triggers ANY failure
                for test_k in range(k-1, -1, -1):
                    tr_fi_k_low, tr_core_k_low, tr_fo_k_low, _ = truncated_reduced_cost_fixing(n, w, v, cap, test_k, W_max, eff_order)
                    mismatch = False
                    for i in range(n):
                        ex_stat = 'C'
                        if i in ex_fi: ex_stat = 'FI'
                        elif i in ex_fo: ex_stat = 'FO'
                        
                        tr_stat_k_low = 'C'
                        if i in tr_fi_k_low: tr_stat_k_low = 'FI'
                        elif i in tr_fo_k_low: tr_stat_k_low = 'FO'
                        
                        if ex_stat != tr_stat_k_low:
                            mismatch = True
                            break
                    if mismatch:
                        k_minus_1_mismatches.append(test_k - k) # Store the offset
                        break
                            
    print("\nResults:")
    print(f"Total instances checked: {len(generators) * len(n_values) * num_trials}")
    print(f"Total T values changed by exact int math: {total_t_mismatches}")
    print(f"Total items checked: {total_items}")
    print(f"Total mismatches at proper k: {len(mismatches)}")
    
    if mismatches:
        for m in mismatches[:10]:
            print(f"Mismatch in {m['instance_type']}: item {m['item']} EXACT={m['exact_status']} TRUNCATED={m['truncated_status']}")
            
    if k_minus_1_mismatches:
        highest_failing_offset = max(k_minus_1_mismatches)
        print(f"Highest failing precision offset: k{highest_failing_offset}")
    else:
        print("Did lower k stress tests produce failures?: NO (even at k=0!)")
    
    # Save raw results
    os.makedirs(os.path.join(os.path.dirname(__file__), 'raw_results'), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), 'raw_results', 'verification_mismatches.json'), 'w') as f:
        json.dump(mismatches, f, indent=2)

if __name__ == "__main__":
    run_verification()

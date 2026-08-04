"""
Adversarial checks for the Core Containment Theorem.

Test 1: No-split-shift condition VIOLATED — check whether containment
        (RC-core ⊆ delta-band-core) fails or happens to hold anyway.

Test 2: Clean instance where all hypotheses hold — verify containment.
"""

def solve_lp(weights, values, capacity, exclude=None, force_in=None):
    """Compute exact LP relaxation bound.
    
    exclude: index of item to remove entirely (force OUT)
    force_in: index of item to force IN (subtract its weight from cap, add its value)
    """
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
    
    # Sort remaining by efficiency
    eff = [(values[k] / weights[k], k) for k in indices]
    eff.sort(reverse=True)
    
    z = base_val
    rem = cap
    for e, k in eff:
        if rem <= 0:
            break
        if weights[k] <= rem:
            rem -= weights[k]
            z += values[k]
        else:
            z += e * rem
            rem = 0
            break
    return z


def find_split(weights, values, capacity):
    """Find split item s, residual R, and Z_LP."""
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
    
    return split_idx, R, z_lp, order


def greedy_lb(weights, values, capacity):
    """Greedy lower bound."""
    n = len(weights)
    eff = [(values[i] / weights[i], i) for i in range(n)]
    eff.sort(reverse=True)
    rem = capacity
    z = 0
    for _, k in eff:
        if weights[k] <= rem:
            rem -= weights[k]
            z += values[k]
    return z


def rc_core(weights, values, capacity):
    """Compute the reduced-cost core (Algorithm 1)."""
    n = len(weights)
    z_lb = greedy_lb(weights, values, capacity)
    s, R, z_lp, order = find_split(weights, values, capacity)
    e_s = values[s] / weights[s]
    
    F1, F0, C = [], [], []
    for i in range(n):
        e_i = values[i] / weights[i]
        if e_i > e_s or (e_i == e_s and i < s):
            # i < s in efficiency order (fully included in LP)
            z_prime = solve_lp(weights, values, capacity, exclude=i)
            if z_prime < z_lb:
                F1.append(i)
            else:
                C.append(i)
        elif i == s:
            C.append(i)  # split item always in core
        else:
            # i > s in efficiency order (excluded in LP)
            z_prime = solve_lp(weights, values, capacity, force_in=i)
            if z_prime < z_lb:
                F0.append(i)
            else:
                C.append(i)
    
    return F1, C, F0, z_lb, z_lp, s, R, e_s


def delta_band_core(weights, values, s, e_s, delta):
    """Compute the delta-band core (Definition 3)."""
    n = len(weights)
    C_delta = []
    for i in range(n):
        e_i = values[i] / weights[i]
        if abs(e_i - e_s) <= delta * e_s:
            C_delta.append(i)
    return C_delta


print("=" * 80)
print("TEST 1: No-split-shift condition VIOLATED")
print("=" * 80)
# Instance where some item i < s has w_i > w_s - R
# Use: w = [25, 10, 15, 8, 5], v = [250, 90, 120, 48, 25]
# e = [10, 9, 8, 6, 5], W = 40
# Order: 0(e=10), 1(e=9), 2(e=8), 3(e=6), 4(e=5)
# cum: 25, 35, 50 > 40. Split s=2, R = 40 - 35 = 5.
# w_s - R = 15 - 5 = 10.
# Item 0: w_0 = 25 > 10. VIOLATES no-split-shift.

w1 = [25, 10, 15, 8, 5]
v1 = [250, 90, 120, 48, 25]
W1 = 40

F1, C_rc, F0, z_lb, z_lp, s, R, e_s = rc_core(w1, v1, W1)
print(f"  Weights:    {w1}")
print(f"  Values:     {v1}")
print(f"  Capacity:   {W1}")
print(f"  Split item: {s} (w_s={w1[s]}, e_s={e_s})")
print(f"  R = {R}, w_s - R = {w1[s] - R}")
print(f"  Z_LP = {z_lp}, Z_LB = {z_lb}")
print(f"  F1 = {F1}, Core = {C_rc}, F0 = {F0}")

# Check no-split-shift for each item in core that's before split
for i in C_rc:
    e_i = v1[i] / w1[i]
    if e_i > e_s:
        print(f"  Item {i}: w_i={w1[i]}, e_i={e_i}, w_i <= w_s-R? {w1[i] <= w1[s] - R}")

# Compute delta* = (Z_LP - Z_LB) / (w_min * e_s)
w_min = min(w1)
gap = z_lp - z_lb
delta_star = gap / (w_min * e_s)
print(f"\n  LP gap = {gap}")
print(f"  w_min = {w_min}, delta* = {delta_star:.6f}")

C_delta = delta_band_core(w1, v1, s, e_s, delta_star)
print(f"  Delta-band core (delta={delta_star:.4f}): {C_delta}")
print(f"  RC core: {C_rc}")
print(f"  Containment (RC ⊆ delta-band)? {set(C_rc).issubset(set(C_delta))}")

# Per-item delta check
print(f"\n  Per-item analysis:")
for i in range(len(w1)):
    e_i = v1[i] / w1[i]
    delta_i = gap / (w1[i] * e_s)
    print(f"    Item {i}: e_i={e_i:.2f}, |e_i - e_s|={abs(e_i-e_s):.2f}, "
          f"delta_i(needed)={abs(e_i-e_s)/e_s:.4f}, "
          f"delta_i(available)={delta_i:.4f}, "
          f"in RC-core={i in C_rc}, in delta-band={i in C_delta}")


print()
print("=" * 80)
print("TEST 2: All hypotheses hold — clean instance")
print("=" * 80)
# All items have small weights relative to w_s - R and R
w2 = [3, 4, 5, 6, 7, 8, 9, 10]
v2 = [30, 36, 40, 42, 42, 40, 36, 30]
# e = [10, 9, 8, 7, 6, 5, 4, 3]
W2 = 20

F1b, C_rc2, F0b, z_lb2, z_lp2, s2, R2, e_s2 = rc_core(w2, v2, W2)
print(f"  Weights:    {w2}")
print(f"  Values:     {v2}")
print(f"  Capacity:   {W2}")
print(f"  Split item: {s2} (w_s={w2[s2]}, e_s={e_s2})")
print(f"  R = {R2}, w_s - R = {w2[s2] - R2}")
print(f"  Z_LP = {z_lp2}, Z_LB = {z_lb2}")
print(f"  F1 = {F1b}, Core = {C_rc2}, F0 = {F0b}")

# Check no-split-shift for each item
for i in range(len(w2)):
    e_i = v2[i] / w2[i]
    if e_i > e_s2 and i != s2:
        nss = w2[i] <= w2[s2] - R2
        print(f"  Item {i} (before split): w_i={w2[i]}, w_i <= w_s-R? {nss} ({w2[i]} <= {w2[s2] - R2})")
    elif e_i < e_s2:
        nss = w2[i] <= R2
        print(f"  Item {i} (after split): w_i={w2[i]}, w_i <= R? {nss} ({w2[i]} <= {R2})")

gap2 = z_lp2 - z_lb2
w_min2 = min(w2)
delta_star2 = gap2 / (w_min2 * e_s2)
print(f"\n  LP gap = {gap2}")
print(f"  w_min = {w_min2}, delta* = {delta_star2:.6f}")

C_delta2 = delta_band_core(w2, v2, s2, e_s2, delta_star2)
print(f"  Delta-band core (delta={delta_star2:.4f}): {C_delta2}")
print(f"  RC core: {C_rc2}")
print(f"  Containment (RC ⊆ delta-band)? {set(C_rc2).issubset(set(C_delta2))}")

print()
print("=" * 80)
print("TEST 3: Specifically designed to check if containment FAILS")
print("         when no-split-shift is violated")
print("=" * 80)

# We need an instance where:
# 1. Some item i has w_i > w_s - R (violates no-split-shift)
# 2. The TRUE Z'_i (with split shift) is HIGHER than what the formula predicts
#    This could mean the item stays in RC-core but the formula-based delta
#    doesn't cover it.
# 
# When no-split-shift is violated, the TRUE Z'_i can be either:
# - LOWER than the formula (because the new split item has lower efficiency)
#   -> This means MORE items get fixed (tighter bound), containment still works
# - HIGHER than the formula... this would need the new split to have HIGHER
#   efficiency, which contradicts the ordering. Actually NO — when we remove
#   item i < s, freed capacity fills s completely, then spills to s+1.
#   The new fractional item is s+1 with e_{s+1} < e_s.
#   So true Z'_i = sum_{j<s,j!=i} v_j + v_s + e_{s+1} * (leftover)
#   This is LESS than what the formula gives (formula uses e_s for ALL freed cap).
#
# So when the no-split-shift condition is violated:
#   True Z'_i < Formula Z'_i (because the spilled capacity earns e_{s+1} < e_s)
#   This means the TRUE drop is LARGER, so MORE items get fixed.
#   Containment should STILL hold (or even be tighter).
#
# Let me verify this reasoning with a concrete example.

# Same as the violating example from Test 1, but let's trace carefully
# w = [25, 10, 15, 8, 5], v = [250, 90, 120, 48, 25], W=40
# s=2 (w=15, e=8), R=5
# Item 0: w_0=25, violates 25 <= 15-5=10
# Formula Z'_0 = Z_LP - 25*(10-8) = Z_LP - 50
# True Z'_0: exclude item 0, items left: 1(e=9,w=10), 2(e=8,w=15), 3(e=6,w=8), 4(e=5,w=5)
# cum: 10, 25, 33, 38 <= 40. Split at... all fit? 10+15+8+5 = 38 <= 40. No split!
# Z'_0 = 90 + 120 + 48 + 25 = 283 (all items fit, LP = IP)

z_true = solve_lp(w1, v1, W1, exclude=0)
print(f"  Item 0 in Test 1: True Z'_0 = {z_true}")
print(f"  Formula Z'_0 = {z_lp - 25*(10-8)}")
print(f"  True Z'_0 < Formula Z'_0? {z_true < z_lp - 25*(10-8)}")

# So true Z'_0 = 283, formula = Z_LP - 50
# Z_LP = 250 + 90 + 8*5 = 380
# Formula = 380 - 50 = 330
# True = 283
# True < Formula, so the true drop is LARGER.
# If Z_LB = 283, then true Z'_0 = Z_LB, item 0 stays in core.
# Formula would say Z'_0 = 330 > Z_LB, also stays in core.
# Both agree. The formula OVERESTIMATES Z'_i, meaning it is LESS aggressive
# about fixing. So the formula-based delta is WIDER than needed.
# Containment (RC ⊆ delta-band) should still hold.

print(f"\n  Z_LP = {z_lp}")
print(f"  In this instance, RC-core = {C_rc}")
print(f"  Since true Z'_i <= formula Z'_i when split shifts,")
print(f"  the RC algorithm fixes AT LEAST as many items as the formula predicts.")
print(f"  Therefore containment (RC-core ⊆ delta-band) cannot be violated by")
print(f"  a split shift — the split shift only makes fixing MORE aggressive.")

# Let me also check the symmetric case: j > s, force IN, w_j > R
# When we force j IN and w_j > R, we consume all of R from s, then
# steal from s-1 (higher efficiency). The true Z'_j drops MORE than 
# the formula predicts (because we lose efficiency e_{s-1} > e_s on the
# stolen capacity, not just e_s).
print(f"\n  Symmetric check: item 3 (j>s, w_j=8, e_j=6) forced IN")
z_true_3 = solve_lp(w1, v1, W1, force_in=3)
z_formula_3 = z_lp - w1[3] * (e_s - v1[3]/w1[3])
print(f"  True Z'_3 = {z_true_3}")
print(f"  Formula Z'_3 = {z_formula_3}")
print(f"  w_3={w1[3]} <= R={R}? {w1[3] <= R}")
# Item 3 has w=8, R=5, so violates condition

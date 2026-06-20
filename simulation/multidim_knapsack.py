"""
Extension to d-dimensional knapsack (Tier 3.3)
===============================================
Extends the LP-fixing + quantum B&B framework to the d-dimensional 0/1
knapsack problem, where each item has d weight components and there are
d capacity constraints.

  max  sum_i v_i x_i
  s.t. sum_i w_{ij} x_i <= W_j   for j = 1..d
       x_i in {0, 1}

The LP relaxation extends naturally: sort by efficiency (using the bottleneck
constraint), fix variables via reduced-cost analysis on the d-dimensional LP
bound. The quantum oracle needs d weight accumulator registers instead of 1.

Key theoretical result:
  - The framework generalizes cleanly to d dimensions
  - Core size α tends to be LARGER for d > 1 (more constraints = harder to fix)
  - This makes the quantum Phase 2 MORE important for d-dimensional knapsack
  - Complexity: O(n · d + sqrt(T_LP) · poly(m, d, log W))
  - No prior work has analyzed LP-fixing + quantum B&B for d-dimensional knapsack

This module demonstrates the theoretical analysis with small-scale experiments.
"""

from __future__ import annotations

import json
import math
from typing import List, Optional, Tuple

import numpy as np


# ============================================================
# d-dimensional LP relaxation and variable fixing
# ============================================================

def _efficiency_order_multidim(weights_d, values, capacities):
    """Sort items by efficiency using the bottleneck constraint.

    For d-dimensional knapsack, we use the "aggregate weight" approach:
    w_agg_i = max_j(w_{ij} / W_j) — the tightest constraint fraction.
    Efficiency = v_i / w_agg_i.
    """
    n = len(values)
    d = len(capacities)
    eff = []
    for i in range(n):
        w_agg = max(weights_d[i][j] / max(capacities[j], 1e-12) for j in range(d))
        eff.append(values[i] / max(w_agg, 1e-12))
    return sorted(range(n), key=lambda i: eff[i], reverse=True)


def _lp_bound_multidim(cum_w, cum_v, capacities, item_indices, weights_d, values):
    """Valid fractional upper bound for d-dimensional knapsack.

    For each constraint j, compute the Dantzig bound using items sorted by
    v_i/w_{ij} (per-constraint efficiency). The minimum across all d constraints
    is a valid upper bound on the LP optimum.

    Research note: This is a SURROGATE relaxation. Each per-constraint Dantzig
    bound is the exact LP optimum of the single-constraint-j relaxation.
    Since each single-constraint relaxation is itself a relaxation of the
    d-constraint problem, min_j(Dantzig_j) is a valid upper bound.
    """
    d = len(capacities)
    if not item_indices:
        return cum_v

    bounds = []
    for j in range(d):
        rem_j = capacities[j] - cum_w[j]
        if rem_j < 0:
            return -math.inf
        # Sort items by v_i/w_{ij} for THIS constraint (valid Dantzig order)
        sorted_items = sorted(item_indices,
                              key=lambda i: values[i] / max(weights_d[i][j], 1e-12),
                              reverse=True)
        bound_j = cum_v
        rem = rem_j
        for i in sorted_items:
            wi_j = weights_d[i][j]
            if wi_j <= rem:
                rem -= wi_j
                bound_j += values[i]
            else:
                bound_j += values[i] * rem / max(wi_j, 1e-12)
                break
        bounds.append(bound_j)
    return min(bounds)  # tightest bound across all constraints


def lp_fix_multidim(weights_d, values, capacities):
    """Reduced-cost variable fixing for d-dimensional knapsack.

    Uses surrogate LP bounds (min of per-constraint Dantzig bounds) which are
    provably valid upper bounds. When UB(exclude_i) < LB, item i must be in
    every optimal solution (fix to 1). When UB(force_i) < LB, item i cannot
    be in any optimal solution (fix to 0).

    Returns (F1, core_indices, F0, residual_caps, V_fixed).
    """
    n = len(values)
    d = len(capacities)
    order = _efficiency_order_multidim(weights_d, values, capacities)

    # Greedy lower bound (valid for any ordering)
    rem = list(capacities)
    z_lb = 0
    greedy_sol = []
    for i in order:
        feasible = all(weights_d[i][j] <= rem[j] for j in range(d))
        if feasible:
            for j in range(d):
                rem[j] -= weights_d[i][j]
            z_lb += values[i]
            greedy_sol.append(i)

    # Find split item (first item rejected by bottleneck constraint)
    cum_w_all = [0.0] * d
    split_idx = -1
    for i in order:
        feasible = all(cum_w_all[j] + weights_d[i][j] <= capacities[j] for j in range(d))
        if feasible:
            for j in range(d):
                cum_w_all[j] += weights_d[i][j]
        else:
            split_idx = i
            break

    F1, F0, core = [], [], []
    for i in order:
        remaining_excl = [x for x in order if x != i]

        # Determine if item is "before" or "after" split in aggregate ordering
        eff_i = values[i] / max(max(weights_d[i][j] / max(capacities[j], 1e-12)
                                    for j in range(d)), 1e-12)
        eff_s = 0.0
        if split_idx >= 0:
            eff_s = values[split_idx] / max(max(weights_d[split_idx][j] /
                    max(capacities[j], 1e-12) for j in range(d)), 1e-12)

        if eff_i > eff_s:
            # Item likely in LP solution; check if excluding it reduces UB below LB
            z_excl = _lp_bound_multidim([0.0]*d, 0.0, capacities,
                                         remaining_excl, weights_d, values)
            if z_excl < z_lb:
                F1.append(i)
            else:
                core.append(i)
        else:
            # Item likely not in LP solution; check if forcing it reduces UB below LB
            cum_forced = list(weights_d[i])
            v_forced = values[i]
            if all(cum_forced[j] <= capacities[j] for j in range(d)):
                z_forced = _lp_bound_multidim(cum_forced, v_forced, capacities,
                                               remaining_excl, weights_d, values)
                if z_forced < z_lb:
                    F0.append(i)
                else:
                    core.append(i)
            else:
                F0.append(i)  # infeasible alone -> can't be in optimal

    res_caps = list(capacities)
    v_fixed = 0
    for i in F1:
        for j in range(d):
            res_caps[j] -= weights_d[i][j]
        v_fixed += values[i]

    return F1, core, F0, res_caps, v_fixed


def dp_multidim(weights_d, values, capacities):
    """Exact DP for d-dimensional knapsack (exponential in capacities).

    Only feasible for small capacities. Uses nested dict for sparse storage.
    """
    n = len(values)
    d = len(capacities)

    if d == 1:
        dp = [0] * (capacities[0] + 1)
        for i in range(n):
            wi, vi = weights_d[i][0], values[i]
            for c in range(capacities[0], wi - 1, -1):
                dp[c] = max(dp[c], dp[c - wi] + vi)
        return dp[capacities[0]]

    # For d=2, use 2D DP
    if d == 2:
        W1, W2 = capacities[0], capacities[1]
        if W1 * W2 > 10**7:
            return _brute_force_multidim(weights_d, values, capacities)
        dp = [[0] * (W2 + 1) for _ in range(W1 + 1)]
        for i in range(n):
            w1, w2 = weights_d[i][0], weights_d[i][1]
            vi = values[i]
            for c1 in range(W1, w1 - 1, -1):
                for c2 in range(W2, w2 - 1, -1):
                    dp[c1][c2] = max(dp[c1][c2], dp[c1 - w1][c2 - w2] + vi)
        return dp[W1][W2]

    return _brute_force_multidim(weights_d, values, capacities)


def _brute_force_multidim(weights_d, values, capacities):
    """Brute-force for small instances."""
    n = len(values)
    d = len(capacities)
    best = 0
    for mask in range(1 << n):
        w = [0] * d
        v = 0
        for i in range(n):
            if mask & (1 << i):
                for j in range(d):
                    w[j] += weights_d[i][j]
                v += values[i]
        if all(w[j] <= capacities[j] for j in range(d)) and v > best:
            best = v
    return best


def bb_nodes_multidim(weights_d, values, capacities, order=None):
    """Count B&B nodes for d-dimensional knapsack with LP bounding."""
    n = len(values)
    d = len(capacities)
    if order is None:
        order = _efficiency_order_multidim(weights_d, values, capacities)

    opt = dp_multidim(weights_d, values, capacities)
    suffix = [order[k:] for k in range(n + 1)]

    # Decision problem: value >= opt
    stack = [(0, [0.0]*d, 0.0)]
    nodes = 0
    while stack:
        k, cw, cv = stack.pop()
        nodes += 1
        if nodes > 10**6:
            return nodes
        if k == n:
            continue
        ub = _lp_bound_multidim(cw, cv, capacities, suffix[k], weights_d, values)
        if ub < opt - 1e-9:
            continue
        item = order[k]
        # Exclude
        stack.append((k + 1, list(cw), cv))
        # Include if feasible
        new_cw = [cw[j] + weights_d[item][j] for j in range(d)]
        if all(new_cw[j] <= capacities[j] for j in range(d)):
            stack.append((k + 1, new_cw, cv + values[item]))
    return nodes


# ============================================================
# Instance generators for d-dimensional knapsack
# ============================================================

def gen_multidim(n, d, seed, R=100):
    """Generate a d-dimensional uncorrelated knapsack instance."""
    rng = np.random.RandomState(seed)
    weights_d = [[int(rng.randint(1, R + 1)) for _ in range(d)] for _ in range(n)]
    values = [int(rng.randint(1, R + 1)) for _ in range(n)]
    capacities = [int(0.5 * sum(weights_d[i][j] for i in range(n))) for j in range(d)]
    return weights_d, values, capacities


# ============================================================
# Experiments
# ============================================================

def run():
    print("=" * 100)
    print("MULTIDIMENSIONAL KNAPSACK EXTENSION (Tier 3.3)")
    print("=" * 100)

    results = []

    print(f"\n{'d':>3} {'n':>3} {'α_avg':>7} {'|F1|':>5} {'|F0|':>5} {'|C|':>5} "
          f"{'BB_nodes':>10} {'√BB':>8} {'correct':>8}")
    print("-" * 100)

    for d in [1, 2, 3, 4]:
        for n in [10, 14, 18]:
            rows = []
            for seed in range(8):
                wd, v, caps = gen_multidim(n, d, seed=3000 + d * 100 + seed)

                # LP fixing
                F1, core, F0, res_caps, v_fixed = lp_fix_multidim(wd, v, caps)
                m = len(core)
                alpha = m / n

                # Exact optimum
                if n <= 20:
                    opt = dp_multidim(wd, v, caps)
                else:
                    opt = None

                # B&B nodes on core
                if m <= 20:
                    core_wd = [wd[i] for i in core]
                    core_v = [v[i] for i in core]
                    bb = bb_nodes_multidim(core_wd, core_v, res_caps)
                else:
                    bb = None

                # Verify fixing correctness
                if opt is not None and m <= 20:
                    core_opt = dp_multidim(core_wd, core_v, res_caps)
                    total = v_fixed + core_opt
                    correct = (total == opt)
                else:
                    correct = None

                rows.append({
                    "d": d, "n": n, "m": m, "alpha": alpha,
                    "F1": len(F1), "F0": len(F0), "core": m,
                    "bb_nodes": bb, "correct": correct,
                })

            avg_alpha = np.mean([r["alpha"] for r in rows])
            avg_F1 = np.mean([r["F1"] for r in rows])
            avg_F0 = np.mean([r["F0"] for r in rows])
            avg_m = np.mean([r["m"] for r in rows])
            bb_vals = [r["bb_nodes"] for r in rows if r["bb_nodes"] is not None]
            avg_bb = np.mean(bb_vals) if bb_vals else float('nan')
            correct_count = sum(1 for r in rows if r["correct"] is True)
            total_checked = sum(1 for r in rows if r["correct"] is not None)

            print(f"{d:>3} {n:>3} {avg_alpha:>7.3f} {avg_F1:>5.1f} {avg_F0:>5.1f} "
                  f"{avg_m:>5.1f} {avg_bb:>10.0f} {math.sqrt(avg_bb) if not math.isnan(avg_bb) else float('nan'):>8.1f} "
                  f"{correct_count}/{total_checked:>3}")
            results.extend(rows)

    # Summary: how α changes with d
    print("\n" + "=" * 60)
    print("SUMMARY: Core ratio α vs. number of constraints d")
    print("=" * 60)
    for d in [1, 2, 3, 4]:
        d_rows = [r for r in results if r["d"] == d]
        avg_alpha = np.mean([r["alpha"] for r in d_rows])
        print(f"  d={d}: avg α = {avg_alpha:.3f}")

    with open("multidim_results.json", "w") as f:
        json.dump({"results": results}, f, indent=2)
    print("\nSaved -> multidim_results.json")


if __name__ == "__main__":
    run()

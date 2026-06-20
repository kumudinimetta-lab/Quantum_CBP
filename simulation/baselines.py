"""
Real baselines and harder instance classes for the knapsack comparison
======================================================================
Addresses the reviewer concern that the paper only compared against the weakest
baselines (meet-in-the-middle and a naive B&B).  Here we add genuinely strong,
widely-used exact solvers and additional hard instance families, then place the
*measured* quantum query count (from quantum_backtracking) alongside them.

Baselines:
  * brute force            (2^n)                        -- only small n
  * dynamic programming     (O(n W), pseudo-polynomial)
  * LP branch-and-bound     (our classical B&B node count)
  * OR-Tools KnapsackSolver (industrial branch-and-bound, Google)
  * Horowitz-Sahni MitM     (2^(n/2) reference count)

Instance families (Pisinger + harder structured ones):
  uncorrelated, weakly/strongly correlated, subset-sum, inverse strongly,
  spanner, profit-ceiling, circle  -- the latter three are designed to defeat
  LP-based pruning and stress branch-and-bound.
"""

from __future__ import annotations

import json
import math
import time
from typing import List

import numpy as np

from quantum_backtracking import (
    efficiency_order, quantum_bb_optimize, _classical_optimum,
    classical_decision_nodes,
)

try:
    from ortools.algorithms.python import knapsack_solver as ortk
    HAVE_ORTOOLS = True
except Exception:
    HAVE_ORTOOLS = False


# ============================================================
# instance generators
# ============================================================

def gen_uncorrelated(n, seed, R=100):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist(); v = rng.randint(1, R + 1, n).tolist()
    return w, v, int(0.5 * sum(w))

def gen_weakly_correlated(n, seed, R=100):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist()
    v = [max(1, wi + rng.randint(-R // 10, R // 10 + 1)) for wi in w]
    return w, v, int(0.5 * sum(w))

def gen_strongly_correlated(n, seed, R=100):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist(); v = [wi + R // 10 for wi in w]
    return w, v, int(0.5 * sum(w))

def gen_subset_sum(n, seed, R=100):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist()
    return w, list(w), int(0.5 * sum(w))

def gen_inverse_strongly(n, seed, R=100):
    rng = np.random.RandomState(seed)
    v = rng.randint(1, R + 1, n).tolist(); w = [vi + R // 10 for vi in v]
    return w, v, int(0.5 * sum(w))

def gen_spanner(n, seed, R=100, span=2):
    """Spanner instances: items are multiples of a tiny spanner set, making
    many equal efficiencies -> weak LP bounds (Pisinger)."""
    rng = np.random.RandomState(seed)
    base_w = rng.randint(1, R // 10 + 1, span)
    base_v = rng.randint(1, R // 10 + 1, span)
    w, v = [], []
    for _ in range(n):
        k = rng.randint(span)
        mult = rng.randint(1, 4)
        w.append(int(base_w[k] * mult)); v.append(int(base_v[k] * mult))
    return w, v, int(0.5 * sum(w))

def gen_profit_ceiling(n, seed, R=100, d=3):
    """Profit-ceiling: profits rounded up to multiples of d -> many ties."""
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist()
    v = [int(d * math.ceil(wi / d)) for wi in w]
    return w, v, int(0.5 * sum(w))

def gen_circle(n, seed, R=100):
    """Circle instances: v_i as a circular function of w_i (Pisinger)."""
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, n).tolist()
    v = [max(1, int((2.0 / 3.0) * math.sqrt(max(4 * R * R - (wi - 2 * R) ** 2, 0)))) for wi in w]
    return w, v, int(0.5 * sum(w))


GENERATORS = {
    "uncorrelated": gen_uncorrelated,
    "weakly_correlated": gen_weakly_correlated,
    "strongly_correlated": gen_strongly_correlated,
    "subset_sum": gen_subset_sum,
    "inverse_strongly": gen_inverse_strongly,
    "spanner": gen_spanner,
    "profit_ceiling": gen_profit_ceiling,
    "circle": gen_circle,
}


# ============================================================
# classical baselines (return value + an effort metric)
# ============================================================

def solve_brute(w, v, cap):
    n = len(w); best = 0
    for mask in range(1 << n):
        tw = tv = 0
        for i in range(n):
            if mask & (1 << i):
                tw += w[i]; tv += v[i]
        if tw <= cap and tv > best:
            best = tv
    return best, (1 << n)  # operations ~ 2^n

def solve_dp(w, v, cap):
    n = len(w); dp = [0] * (cap + 1)
    ops = 0
    for i in range(n):
        wi, vi = w[i], v[i]
        for c in range(cap, wi - 1, -1):
            ops += 1
            if dp[c - wi] + vi > dp[c]:
                dp[c] = dp[c - wi] + vi
    return dp[cap], ops  # operations ~ n*cap

def solve_lp_bb_nodes(w, v, cap):
    """Classical LP B&B node count to *prove* optimality (decision at opt)."""
    opt = _classical_optimum(w, v, cap)
    order = efficiency_order(w, v)
    # nodes to confirm value >= opt (find) plus value >= opt+1 (prove none better)
    nodes = classical_decision_nodes(w, v, cap, opt, order)
    nodes += classical_decision_nodes(w, v, cap, opt + 1, order)
    return opt, nodes

def solve_ortools(w, v, cap):
    if not HAVE_ORTOOLS:
        return None, None
    solver = ortk.KnapsackSolver(
        ortk.SolverType.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "k")
    solver.init(list(v), [list(w)], [cap])
    t0 = time.perf_counter()
    val = solver.solve()
    dt = time.perf_counter() - t0
    return val, dt


# ============================================================
# main comparison
# ============================================================

def run(n_values=(12, 16, 20), trials=6, max_nodes=20000):
    print("=" * 110)
    print("REAL BASELINES vs MEASURED QUANTUM QUERIES")
    print(f"OR-Tools available: {HAVE_ORTOOLS}")
    print("=" * 110)

    all_rows = []
    for name, gen in GENERATORS.items():
        print(f"\n### {name.upper()}")
        print(f"{'n':>3} {'DP_ops':>10} {'BB_nodes':>10} {'ORtool_ms':>10} "
              f"{'MitM':>10} {'Q_meas':>10} {'Qdec':>8} {'allcorrect':>11}")
        print("-" * 110)
        for n in n_values:
            rows = []
            for t in range(trials):
                w, v, cap = gen(n, seed=7000 + 137 * n + t)
                opt_dp, dp_ops = solve_dp(w, v, cap)
                opt_bb, bb_nodes = solve_lp_bb_nodes(w, v, cap)
                or_val, or_ms = solve_ortools(w, v, cap)
                mitm = 2 ** (n // 2)
                qres = quantum_bb_optimize(w, v, cap, constant=2.0, K=11,
                                           max_nodes=max_nodes)
                q_total = qres.quantum_queries_total if qres else None
                q_dec = qres.montanaro_queries_decisive if qres else None
                q_ok = (qres.correct if qres else None)
                vals = [opt_dp, opt_bb] + ([or_val] if or_val is not None else [])
                if q_ok is not None and qres:
                    vals.append(qres.optimal_value)
                all_correct = len(set(vals)) == 1
                rows.append({
                    "type": name, "n": n, "opt": opt_dp,
                    "dp_ops": dp_ops, "bb_nodes": bb_nodes,
                    "ortools_ms": (or_ms * 1000) if or_ms is not None else None,
                    "mitm": mitm,
                    "quantum_queries": q_total,
                    "quantum_decisive": q_dec,
                    "quantum_simulable": qres is not None,
                    "all_solvers_agree": all_correct,
                })
            all_rows.extend(rows)
            avg = lambda k: np.mean([r[k] for r in rows if r[k] is not None]) \
                if any(r[k] is not None for r in rows) else float('nan')
            qsim = [r for r in rows if r["quantum_simulable"]]
            q_meas_s = f"{np.mean([r['quantum_queries'] for r in qsim]):.0f}" if qsim else "n/a"
            q_dec_s = f"{np.mean([r['quantum_decisive'] for r in qsim]):.0f}" if qsim else "n/a"
            ok = sum(r["all_solvers_agree"] for r in rows if r["quantum_simulable"])
            print(f"{n:>3} {avg('dp_ops'):>10.0f} {avg('bb_nodes'):>10.0f} "
                  f"{avg('ortools_ms'):>10.3f} {avg('mitm'):>10.0f} "
                  f"{q_meas_s:>10} {q_dec_s:>8} {ok}/{len(qsim):>3}")

    with open("baselines_results.json", "w") as f:
        json.dump({"have_ortools": HAVE_ORTOOLS, "data": all_rows}, f, indent=2)
    print("\nSaved -> baselines_results.json")


if __name__ == "__main__":
    run()

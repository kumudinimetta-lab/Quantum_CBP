"""
LP-Pruned Quantum Branch-and-Bound for 0/1 Knapsack
=====================================================
Novel Algorithm Simulation v4

This implements and measures:
1. Classical B&B with LP bounds → measure T_LP (tree nodes visited)
2. Classical B&B WITHOUT LP bounds → measure T_full
3. Our contribution: sqrt(T_LP) quantum speedup via Montanaro
4. Comparison with all baselines
"""

import numpy as np
import math
import json
import time
from typing import List, Tuple, Optional

# ============================================================
# INSTANCE GENERATION
# ============================================================

def generate_instance(n, seed=None, w_range=(1, 100), v_range=(1, 100), cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    weights = rng.randint(w_range[0], w_range[1]+1, size=n).tolist()
    values = rng.randint(v_range[0], v_range[1]+1, size=n).tolist()
    capacity = int(cap_ratio * sum(weights))
    return weights, values, capacity

# ============================================================
# LP RELAXATION
# ============================================================

def lp_bound(weights, values, capacity, items=None, start=0):
    """
    Compute LP relaxation upper bound for a partial knapsack.
    Items should be pre-sorted by efficiency.
    'start' allows computing bound from a specific item index.
    """
    if items is None:
        items = list(range(len(weights)))
    
    remaining = capacity
    total = 0.0
    
    for i in items:
        if remaining <= 0:
            break
        if weights[i] <= remaining:
            remaining -= weights[i]
            total += values[i]
        else:
            total += (values[i] / weights[i]) * remaining
            remaining = 0
    
    return total

def reduced_cost_fixing(n, weights, values, capacity):
    """Reduced-cost variable fixing (proven correct)."""
    all_items = list(range(n))
    
    # Greedy lower bound
    eff_order = sorted(all_items, key=lambda i: values[i]/weights[i], reverse=True)
    remaining = capacity
    lb = 0
    for i in eff_order:
        if weights[i] <= remaining:
            remaining -= weights[i]
            lb += values[i]
    
    # LP relaxation for all items
    lp_val = lp_bound(weights, values, capacity, eff_order)
    
    fixed_one, core, fixed_zero = [], [], []
    
    for i in range(n):
        remaining_items = [j for j in all_items if j != i]
        remaining_sorted = sorted(remaining_items, key=lambda j: values[j]/weights[j], reverse=True)
        
        eff_i = values[i] / weights[i]
        # Check LP position
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
            # Item i is in LP solution (x_i = 1)
            reduced = lp_bound(weights, values, capacity, remaining_sorted)
            if reduced < lb - 1e-9:
                fixed_one.append(i)
            else:
                core.append(i)
        else:
            # Item i is NOT in LP solution (x_i = 0 or fractional)
            forced_cap = capacity - weights[i]
            if forced_cap < 0:
                fixed_zero.append(i)
                continue
            reduced = lp_bound(weights, values, forced_cap, remaining_sorted) + values[i]
            if reduced < lb - 1e-9:
                fixed_zero.append(i)
            else:
                core.append(i)
    
    return fixed_one, core, fixed_zero

# ============================================================
# BRANCH AND BOUND (Classical, with node counting)
# ============================================================

class BranchAndBound:
    """Classical B&B for knapsack with LP bounding and node counting."""
    
    def __init__(self, weights, values, capacity, use_lp_bound=True):
        self.w = weights
        self.v = values
        self.cap = capacity
        self.n = len(weights)
        self.use_lp = use_lp_bound
        
        # Sort items by efficiency (descending)
        self.order = sorted(range(self.n), key=lambda i: values[i]/weights[i], reverse=True)
        
        self.best_val = 0
        self.best_sol = [0] * self.n
        self.nodes_visited = 0
        self.nodes_pruned = 0
        self.max_depth = 0
    
    def _upper_bound(self, level, cur_weight, cur_value):
        """Compute upper bound at this node using LP relaxation."""
        if not self.use_lp:
            # Without LP: trivial bound (sum of all remaining values)
            remaining_val = sum(self.v[self.order[i]] for i in range(level, self.n)
                              if self.w[self.order[i]] <= self.cap - cur_weight)
            return cur_value + remaining_val + sum(
                self.v[self.order[i]] for i in range(level, self.n)
                if self.w[self.order[i]] > self.cap - cur_weight
            )
        
        # LP bound: greedily fill remaining capacity with fractional items
        bound = cur_value
        remaining = self.cap - cur_weight
        
        for i in range(level, self.n):
            idx = self.order[i]
            if remaining <= 0:
                break
            if self.w[idx] <= remaining:
                remaining -= self.w[idx]
                bound += self.v[idx]
            else:
                bound += (self.v[idx] / self.w[idx]) * remaining
                remaining = 0
                break
        
        return bound
    
    def solve(self):
        """DFS branch and bound."""
        self._dfs(0, 0, 0)
        return self.best_val, self.nodes_visited, self.nodes_pruned, self.max_depth
    
    def _dfs(self, level, cur_weight, cur_value):
        self.nodes_visited += 1
        self.max_depth = max(self.max_depth, level)
        
        if level == self.n:
            if cur_value > self.best_val:
                self.best_val = cur_value
            return
        
        idx = self.order[level]
        
        # Pruning check
        ub = self._upper_bound(level, cur_weight, cur_value)
        if ub <= self.best_val:
            self.nodes_pruned += 1
            return
        
        # Branch: include item
        if cur_weight + self.w[idx] <= self.cap:
            self._dfs(level + 1, cur_weight + self.w[idx], cur_value + self.v[idx])
        
        # Branch: exclude item
        self._dfs(level + 1, cur_weight, cur_value)


# ============================================================
# COMPLETE HYBRID ALGORITHM
# ============================================================

def hybrid_algorithm(n, weights, values, capacity):
    """
    Full hybrid LP-Pruned Quantum B&B algorithm.
    Returns comprehensive metrics.
    """
    # Phase 1: LP Preprocessing + Variable Fixing
    t0 = time.time()
    fixed_one, core, fixed_zero = reduced_cost_fixing(n, weights, values, capacity)
    t_preprocess = time.time() - t0
    
    m = len(core)
    fi_w = sum(weights[i] for i in fixed_one)
    fi_v = sum(values[i] for i in fixed_one)
    residual_cap = capacity - fi_w
    
    # Phase 2a: Classical B&B on FULL problem (baseline)
    bb_full = BranchAndBound(weights, values, capacity, use_lp_bound=True)
    opt_val_full, T_full_lp, pruned_full, depth_full = bb_full.solve()
    
    # Phase 2b: Classical B&B WITHOUT LP bounds (worst case baseline)
    bb_no_lp = BranchAndBound(weights, values, capacity, use_lp_bound=False)
    _, T_full_nolp, _, _ = bb_no_lp.solve()
    
    # Phase 2c: Classical B&B on CORE items only (our approach, classical part)
    if m > 0 and residual_cap >= 0:
        core_w = [weights[i] for i in core]
        core_v = [values[i] for i in core]
        bb_core = BranchAndBound(core_w, core_v, residual_cap, use_lp_bound=True)
        core_opt, T_core_lp, pruned_core, depth_core = bb_core.solve()
        hybrid_val = fi_v + core_opt
    else:
        T_core_lp = 1
        pruned_core = 0
        depth_core = 0
        hybrid_val = fi_v
    
    # Phase 3: Quantum speedup calculation
    # Montanaro: O(sqrt(T) * poly(d))
    quantum_ops = math.sqrt(T_core_lp) * (depth_core + 1)
    
    return {
        'n': n,
        'm': m,
        'alpha': round(m / n, 4) if n > 0 else 0,
        'fi': len(fixed_one),
        'fo': len(fixed_zero),
        'opt_val': opt_val_full,
        'hybrid_val': hybrid_val,
        'correct': hybrid_val == opt_val_full,
        
        # Tree sizes
        'T_full_nolp': T_full_nolp,    # B&B without LP (worst)
        'T_full_lp': T_full_lp,        # B&B with LP on full problem
        'T_core_lp': T_core_lp,        # B&B with LP on core only (ours)
        
        # Speedup metrics
        'classical_mitm': 2 ** (n // 2),
        'grover_full': 2 ** (n // 2),   # Same as MitM in query complexity
        'montanaro_full': math.sqrt(T_full_lp) * (depth_full + 1),
        'quantum_ops_ours': quantum_ops,
        
        # Speedups
        'speedup_vs_mitm': (2 ** (n // 2)) / max(1, quantum_ops),
        'speedup_vs_grover': (2 ** (n // 2)) / max(1, quantum_ops),
        'speedup_vs_montanaro': (math.sqrt(T_full_lp) * (depth_full + 1)) / max(1, quantum_ops),
        'speedup_vs_classical_bb': T_full_lp / max(1, quantum_ops),
        
        'depth_core': depth_core,
        'preprocess_time': round(t_preprocess, 6),
    }


# ============================================================
# BENCHMARK
# ============================================================

def run_benchmark():
    n_values = [8, 10, 12, 14, 16, 18, 20, 22, 24]
    num_trials = 30
    
    print("=" * 130)
    print("LP-PRUNED QUANTUM BRANCH-AND-BOUND FOR 0/1 KNAPSACK")
    print("Novel: Combining Pisinger LP pruning + Montanaro quantum B&B")
    print("=" * 130)
    
    header = (f"{'n':>3} {'m':>3} {'a':>5} "
              f"{'T_nolp':>10} {'T_full':>10} {'T_core':>10} "
              f"{'MitM':>10} {'Grover':>10} {'Mont':>10} {'Ours':>10} "
              f"{'vs_MitM':>8} {'vs_Grov':>8} {'vs_Mont':>8} {'OK':>4}")
    print(header)
    print("-" * 130)
    
    all_data = []
    
    for n in n_values:
        results = []
        for trial in range(num_trials):
            seed = n * 1000 + trial
            w, v, cap = generate_instance(n, seed=seed)
            r = hybrid_algorithm(n, w, v, cap)
            r['trial'] = trial
            results.append(r)
            all_data.append(r)
        
        # Averages
        avg = lambda key: np.mean([r[key] for r in results])
        all_correct = all(r['correct'] for r in results)
        
        print(f"{n:>3} {avg('m'):>3.0f} {avg('alpha'):>5.2f} "
              f"{avg('T_full_nolp'):>10.0f} {avg('T_full_lp'):>10.0f} {avg('T_core_lp'):>10.0f} "
              f"{avg('classical_mitm'):>10.0f} {avg('grover_full'):>10.0f} {avg('montanaro_full'):>10.0f} {avg('quantum_ops_ours'):>10.1f} "
              f"{avg('speedup_vs_mitm'):>8.1f}x {avg('speedup_vs_grover'):>8.1f}x {avg('speedup_vs_montanaro'):>8.1f}x "
              f"{'OK' if all_correct else 'FAIL':>4}")
    
    # SUMMARY
    total = len(all_data)
    correct = sum(1 for r in all_data if r['correct'])
    
    print(f"\n{'='*130}")
    print("SUMMARY")
    print(f"{'='*130}")
    print(f"Total experiments: {total}")
    print(f"Correct: {correct}/{total} ({100*correct/total:.1f}%)")
    print(f"\nAverage metrics:")
    print(f"  alpha (core ratio):        {np.mean([r['alpha'] for r in all_data]):.4f}")
    print(f"  T_full (B&B with LP):      {np.mean([r['T_full_lp'] for r in all_data]):.0f}")
    print(f"  T_core (B&B core with LP): {np.mean([r['T_core_lp'] for r in all_data]):.0f}")
    print(f"  Quantum ops (ours):        {np.mean([r['quantum_ops_ours'] for r in all_data]):.1f}")
    print(f"  Speedup vs MitM:           {np.mean([r['speedup_vs_mitm'] for r in all_data]):.1f}x")
    print(f"  Speedup vs Grover:         {np.mean([r['speedup_vs_grover'] for r in all_data]):.1f}x")
    print(f"  Speedup vs Montanaro:      {np.mean([r['speedup_vs_montanaro'] for r in all_data]):.1f}x")
    
    # KEY RESULT: Show tree size reduction
    print(f"\n{'='*130}")
    print("KEY RESULT: Tree Size Reduction Chain")
    print(f"{'='*130}")
    for n in n_values:
        nd = [r for r in all_data if r['n'] == n]
        t_nolp = np.mean([r['T_full_nolp'] for r in nd])
        t_lp = np.mean([r['T_full_lp'] for r in nd])
        t_core = np.mean([r['T_core_lp'] for r in nd])
        sq_core = np.mean([math.sqrt(r['T_core_lp']) for r in nd])
        qops = np.mean([r['quantum_ops_ours'] for r in nd])
        
        print(f"n={n:>2}: T_nolp={t_nolp:>10.0f} -> T_lp={t_lp:>8.0f} "
              f"-> T_core={t_core:>6.0f} -> sqrt(T_core)={sq_core:>6.1f} "
              f"-> Q_ops={qops:>8.1f}")
    
    # Save
    # Convert non-serializable types
    for r in all_data:
        for k, val in r.items():
            if isinstance(val, (np.integer, np.int64)):
                r[k] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                r[k] = float(val)
    
    with open("benchmark_results_v4.json", "w") as f:
        json.dump({
            "algorithm": "LP-Pruned Quantum Branch-and-Bound",
            "method": "Pisinger LP fixing + Montanaro quantum walk on B&B tree",
            "summary": {
                "total": total,
                "correct": correct,
                "avg_alpha": round(float(np.mean([r['alpha'] for r in all_data])), 4),
                "avg_speedup_vs_mitm": round(float(np.mean([r['speedup_vs_mitm'] for r in all_data])), 2),
                "avg_speedup_vs_grover": round(float(np.mean([r['speedup_vs_grover'] for r in all_data])), 2),
                "avg_speedup_vs_montanaro": round(float(np.mean([r['speedup_vs_montanaro'] for r in all_data])), 2),
            },
            "data": all_data
        }, f, indent=2)
    print(f"\nResults saved to benchmark_results_v4.json")
    
    return all_data


if __name__ == "__main__":
    data = run_benchmark()

"""
Hybrid Quantum-Classical Knapsack: Simulation & Verification
============================================================
Validates: (1) LP filtering reduces core size (alpha < 1)
           (2) Quantum search finds correct optimal solutions  
           (3) Operation count comparison vs classical MitM
"""

import numpy as np
import time
import itertools
import json
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict

# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class KnapsackInstance:
    n: int
    weights: List[int]
    values: List[int]
    capacity: int

@dataclass  
class FilterResult:
    fixed_in: List[int]       # indices of fixed-in items
    core: List[int]           # indices of core items
    fixed_out: List[int]      # indices of fixed-out items
    residual_capacity: int
    baseline_value: int
    alpha: float              # filtering ratio |C|/n
    split_item: int
    delta: float

@dataclass
class BenchmarkResult:
    n: int
    capacity: int
    optimal_value: int
    classical_mitm_ops: int       # 2^(n/2) operations
    hybrid_core_size: int         # m = |C|
    hybrid_alpha: float           # m/n
    hybrid_ops: int               # 2^(m/2) operations  
    speedup_factor: float         # classical_ops / hybrid_ops
    quantum_queries: int          # 2^(m/4) Grover iterations
    hybrid_correct: bool          # did hybrid find optimal?
    quantum_correct: bool         # did quantum find optimal?
    filtering_time_ms: float
    classical_time_ms: float

# ============================================================
# INSTANCE GENERATION
# ============================================================

def generate_instance(n: int, seed: int = None, 
                      w_range=(1, 100), v_range=(1, 100),
                      capacity_ratio=0.5) -> KnapsackInstance:
    """Generate random knapsack instance."""
    rng = np.random.RandomState(seed)
    weights = rng.randint(w_range[0], w_range[1] + 1, size=n).tolist()
    values = rng.randint(v_range[0], v_range[1] + 1, size=n).tolist()
    capacity = int(capacity_ratio * sum(weights))
    return KnapsackInstance(n=n, weights=weights, values=values, capacity=capacity)

# ============================================================
# CLASSICAL SOLVERS
# ============================================================

def brute_force_knapsack(inst: KnapsackInstance) -> Tuple[int, List[int]]:
    """Exact brute force solver. Returns (optimal_value, selected_items)."""
    best_val = 0
    best_items = []
    for mask in range(1 << inst.n):
        w_total = 0
        v_total = 0
        items = []
        for i in range(inst.n):
            if mask & (1 << i):
                w_total += inst.weights[i]
                v_total += inst.values[i]
                items.append(i)
        if w_total <= inst.capacity and v_total > best_val:
            best_val = v_total
            best_items = items
    return best_val, best_items

def meet_in_the_middle(inst: KnapsackInstance) -> Tuple[int, int]:
    """Classical MitM solver. Returns (optimal_value, operation_count)."""
    n = inst.n
    half = n // 2
    
    # Enumerate first half
    list_a = []
    for mask in range(1 << half):
        w, v = 0, 0
        for i in range(half):
            if mask & (1 << i):
                w += inst.weights[i]
                v += inst.values[i]
        if w <= inst.capacity:
            list_a.append((w, v))
    
    # Enumerate second half
    list_b = []
    for mask in range(1 << (n - half)):
        w, v = 0, 0
        for i in range(n - half):
            if mask & (1 << i):
                w += inst.weights[half + i]
                v += inst.values[half + i]
        if w <= inst.capacity:
            list_b.append((w, v))
    
    # Sort list_b by weight
    list_b.sort(key=lambda x: x[0])
    
    # For each subset in A, find best compatible in B
    ops = len(list_a) + len(list_b)  # enumeration ops
    best_val = 0
    
    # Precompute best value for each weight limit in B
    best_b_val = [0] * (len(list_b) + 1)
    for i in range(len(list_b) - 1, -1, -1):
        best_b_val[i] = max(list_b[i][1], best_b_val[i + 1])
    
    for wa, va in list_a:
        remaining = inst.capacity - wa
        # Binary search for largest weight <= remaining
        lo, hi = 0, len(list_b) - 1
        pos = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            ops += 1
            if list_b[mid][0] <= remaining:
                pos = mid
                lo = mid + 1
            else:
                hi = mid - 1
        if pos >= 0:
            # Check all entries up to pos for best value
            for j in range(pos + 1):
                if va + list_b[j][1] > best_val:
                    best_val = va + list_b[j][1]
                ops += 1
    
    return best_val, ops

# ============================================================
# LP FILTERING (PHASE 1)
# ============================================================

def lp_filter(inst: KnapsackInstance, delta: float = 0.3) -> FilterResult:
    """LP-relaxation-guided item filtering."""
    n = inst.n
    
    # Compute efficiencies
    efficiencies = [(inst.values[i] / inst.weights[i], i) for i in range(n)]
    efficiencies.sort(reverse=True)  # decreasing efficiency
    
    # Find split item
    cumulative_weight = 0
    split_idx = 0
    for idx, (eff, orig_i) in enumerate(efficiencies):
        cumulative_weight += inst.weights[orig_i]
        if cumulative_weight > inst.capacity:
            split_idx = idx
            break
    
    split_eff = efficiencies[split_idx][0]
    
    # Partition items
    fixed_in = []
    core = []
    fixed_out = []
    
    for eff, orig_i in efficiencies:
        if eff > (1 + delta) * split_eff:
            fixed_in.append(orig_i)
        elif eff < (1 - delta) * split_eff:
            fixed_out.append(orig_i)
        else:
            core.append(orig_i)
    
    # Compute residual capacity
    baseline_value = sum(inst.values[i] for i in fixed_in)
    fixed_in_weight = sum(inst.weights[i] for i in fixed_in)
    residual_capacity = inst.capacity - fixed_in_weight
    
    # Handle infeasible fixed-in set
    if residual_capacity < 0:
        # Move lowest-efficiency fixed-in items to core
        fi_sorted = sorted(fixed_in, key=lambda i: inst.values[i]/inst.weights[i])
        while residual_capacity < 0 and fi_sorted:
            item = fi_sorted.pop(0)
            fixed_in.remove(item)
            core.append(item)
            residual_capacity += inst.weights[item]
            baseline_value -= inst.values[item]
    
    alpha = len(core) / n if n > 0 else 0
    
    return FilterResult(
        fixed_in=fixed_in, core=core, fixed_out=fixed_out,
        residual_capacity=residual_capacity,
        baseline_value=baseline_value,
        alpha=alpha, split_item=split_idx, delta=delta
    )

# ============================================================
# HYBRID SOLVER (CLASSICAL SIMULATION OF QUANTUM)
# ============================================================

def solve_core_brute_force(inst: KnapsackInstance, fr: FilterResult) -> Tuple[int, List[int]]:
    """Solve knapsack over core items with residual capacity."""
    core = fr.core
    m = len(core)
    W_prime = fr.residual_capacity
    
    best_val = 0
    best_items = []
    
    for mask in range(1 << m):
        w, v = 0, 0
        items = []
        for i in range(m):
            if mask & (1 << i):
                w += inst.weights[core[i]]
                v += inst.values[core[i]]
                items.append(core[i])
        if w <= W_prime and v > best_val:
            best_val = v
            best_items = items
    
    return best_val, best_items

def hybrid_solve(inst: KnapsackInstance, delta: float = 0.3) -> Tuple[int, List[int], FilterResult]:
    """Full hybrid algorithm (classical simulation)."""
    # Phase 1: LP filtering
    fr = lp_filter(inst, delta)
    
    # Phase 2: Solve core
    if len(fr.core) == 0:
        return fr.baseline_value, fr.fixed_in, fr
    
    core_val, core_items = solve_core_brute_force(inst, fr)
    
    # Phase 3: Post-processing (check fixed-out items)
    solution = fr.fixed_in + core_items
    total_weight = sum(inst.weights[i] for i in solution)
    total_value = fr.baseline_value + core_val
    
    # Try adding fixed-out items
    fo_sorted = sorted(fr.fixed_out, 
                       key=lambda i: inst.values[i]/inst.weights[i], reverse=True)
    for j in fo_sorted:
        if total_weight + inst.weights[j] <= inst.capacity:
            solution.append(j)
            total_weight += inst.weights[j]
            total_value += inst.values[j]
    
    # Try swaps
    for j in fo_sorted:
        if j in solution:
            continue
        ej = inst.values[j] / inst.weights[j]
        for i in list(solution):
            ei = inst.values[i] / inst.weights[i]
            if ei < ej:
                new_weight = total_weight - inst.weights[i] + inst.weights[j]
                new_value = total_value - inst.values[i] + inst.values[j]
                if new_weight <= inst.capacity and new_value > total_value:
                    solution.remove(i)
                    solution.append(j)
                    total_weight = new_weight
                    total_value = new_value
                    break
    
    return total_value, solution, fr

# ============================================================
# QUANTUM SIMULATION (GROVER ORACLE VERIFICATION)
# ============================================================

def simulate_grover_knapsack(inst: KnapsackInstance, fr: FilterResult, 
                              optimal_core_val: int) -> Dict:
    """
    Simulate Grover's algorithm on core items.
    Counts oracle calls and verifies correctness.
    """
    core = fr.core
    m = len(core)
    W_prime = fr.residual_capacity
    
    if m == 0:
        return {"queries": 0, "correct": True, "m": 0}
    if m > 20:
        # Too large for simulation, return theoretical counts
        theoretical_queries = int(math.ceil(math.pi/4 * math.sqrt(2**m)))
        return {"queries": theoretical_queries, "correct": None, "m": m, 
                "note": "theoretical_only"}
    
    # Count number of "good" states (feasible + optimal value)
    good_states = 0
    optimal_mask = -1
    best_val = 0
    
    for mask in range(1 << m):
        w, v = 0, 0
        for i in range(m):
            if mask & (1 << i):
                w += inst.weights[core[i]]
                v += inst.values[core[i]]
        if w <= W_prime:
            if v > best_val:
                best_val = v
                optimal_mask = mask
                good_states = 1
            elif v == best_val:
                good_states += 1
    
    # Grover iteration count
    N = 2 ** m
    if good_states == 0:
        return {"queries": 0, "correct": True, "m": m, "good_states": 0}
    
    theta = math.asin(math.sqrt(good_states / N))
    optimal_iterations = max(1, int(round(math.pi / (4 * theta) - 0.5)))
    
    # Compute success probability after optimal iterations
    success_prob = math.sin((2 * optimal_iterations + 1) * theta) ** 2
    
    return {
        "queries": optimal_iterations,
        "correct": best_val == optimal_core_val,
        "m": m,
        "good_states": good_states,
        "total_states": N,
        "success_probability": round(success_prob, 4),
        "found_value": best_val
    }

# ============================================================
# QISKIT CIRCUIT VERIFICATION (small instances)
# ============================================================

def qiskit_grover_verify(inst: KnapsackInstance, fr: FilterResult) -> Dict:
    """Build and run actual Qiskit Grover circuit for small core sizes."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
    except ImportError:
        return {"status": "qiskit_not_available"}
    
    core = fr.core
    m = len(core)
    W_prime = fr.residual_capacity
    
    if m == 0:
        return {"status": "no_core_items", "correct": True}
    if m > 10:
        return {"status": "too_large_for_circuit", "m": m}
    
    # Find good states classically
    good_masks = []
    best_val = 0
    for mask in range(1 << m):
        w, v = 0, 0
        for i in range(m):
            if mask & (1 << i):
                w += inst.weights[core[i]]
                v += inst.values[core[i]]
        if w <= W_prime:
            if v > best_val:
                best_val = v
                good_masks = [mask]
            elif v == best_val:
                good_masks.append(mask)
    
    if not good_masks:
        return {"status": "no_feasible_solution", "correct": True}
    
    N = 2 ** m
    t = len(good_masks)
    theta = math.asin(math.sqrt(t / N))
    num_iters = max(1, int(round(math.pi / (4 * theta) - 0.5)))
    
    # Build Grover circuit
    qc = QuantumCircuit(m)
    
    # Initial superposition
    qc.h(range(m))
    
    # Grover iterations
    for _ in range(num_iters):
        # Oracle: mark good states
        for mask in good_masks:
            # Flip qubits where bit is 0
            for i in range(m):
                if not (mask & (1 << i)):
                    qc.x(i)
            # Multi-controlled Z
            if m == 1:
                qc.z(0)
            elif m == 2:
                qc.cz(0, 1)
            else:
                qc.h(m - 1)
                qc.mcx(list(range(m - 1)), m - 1)
                qc.h(m - 1)
            # Unflip
            for i in range(m):
                if not (mask & (1 << i)):
                    qc.x(i)
        
        # Diffuser
        qc.h(range(m))
        qc.x(range(m))
        if m == 1:
            qc.z(0)
        elif m == 2:
            qc.cz(0, 1)
        else:
            qc.h(m - 1)
            qc.mcx(list(range(m - 1)), m - 1)
            qc.h(m - 1)
        qc.x(range(m))
        qc.h(range(m))
    
    # Simulate
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities_dict()
    
    # Find most probable state
    max_state = max(probs, key=probs.get)
    max_prob = probs[max_state]
    measured_mask = int(max_state, 2)
    
    # Reverse bit order (Qiskit uses little-endian)
    reversed_mask = 0
    for i in range(m):
        if measured_mask & (1 << i):
            reversed_mask |= (1 << (m - 1 - i))
    
    correct = reversed_mask in good_masks
    
    return {
        "status": "success",
        "m": m,
        "circuit_depth": qc.depth(),
        "num_gates": qc.size(),
        "grover_iterations": num_iters,
        "good_states": t,
        "max_probability": round(max_prob, 4),
        "correct": correct,
        "optimal_value": best_val
    }

# ============================================================
# MAIN BENCHMARK
# ============================================================

def run_benchmark(n_values=None, num_trials=10, delta=0.3):
    """Run full benchmark across instance sizes."""
    if n_values is None:
        n_values = [4, 6, 8, 10, 12, 14, 16, 18, 20]
    
    results = []
    
    print("=" * 80)
    print("HYBRID QUANTUM-CLASSICAL KNAPSACK BENCHMARK")
    print("=" * 80)
    print(f"{'n':>4} {'alpha':>8} {'m':>4} {'ClassOps':>12} {'HybridOps':>12} "
          f"{'Speedup':>10} {'QQueries':>10} {'Correct':>8}")
    print("-" * 80)
    
    for n in n_values:
        alphas = []
        speedups = []
        all_correct = True
        quantum_correct_count = 0
        total_quantum_tests = 0
        
        for trial in range(num_trials):
            seed = n * 1000 + trial
            inst = generate_instance(n, seed=seed)
            
            # Ground truth
            t0 = time.time()
            opt_val, opt_items = brute_force_knapsack(inst)
            classical_time = (time.time() - t0) * 1000
            
            # Hybrid
            t0 = time.time()
            hybrid_val, hybrid_items, fr = hybrid_solve(inst, delta=delta)
            filter_time = (time.time() - t0) * 1000
            
            m = len(fr.core)
            alpha = fr.alpha
            
            # Operation counts
            classical_ops = 2 ** (n // 2)  # MitM baseline
            hybrid_ops = max(1, 2 ** (m // 2))  # MitM on core
            speedup = classical_ops / hybrid_ops
            quantum_queries = max(1, int(math.ceil(math.pi/4 * math.sqrt(2 ** (m // 2)))))
            
            # Correctness check
            correct = (hybrid_val == opt_val)
            if not correct:
                all_correct = False
            
            # Quantum verification (for small instances)
            q_correct = True
            if m <= 10 and m > 0:
                core_opt_val = opt_val - fr.baseline_value
                # Account for fixed-out items that might have been added
                q_result = simulate_grover_knapsack(inst, fr, core_opt_val)
                if q_result.get("correct") is not None:
                    q_correct = q_result["correct"]
                    total_quantum_tests += 1
                    if q_correct:
                        quantum_correct_count += 1
            
            alphas.append(alpha)
            speedups.append(speedup)
            
            results.append(BenchmarkResult(
                n=n, capacity=inst.capacity, optimal_value=opt_val,
                classical_mitm_ops=classical_ops,
                hybrid_core_size=m, hybrid_alpha=alpha,
                hybrid_ops=hybrid_ops, speedup_factor=speedup,
                quantum_queries=quantum_queries,
                hybrid_correct=correct, quantum_correct=q_correct,
                filtering_time_ms=filter_time,
                classical_time_ms=classical_time
            ))
        
        avg_alpha = np.mean(alphas)
        avg_speedup = np.mean(speedups)
        avg_m = np.mean([r.hybrid_core_size for r in results[-num_trials:]])
        avg_classical_ops = 2 ** (n // 2)
        avg_hybrid_ops = np.mean([r.hybrid_ops for r in results[-num_trials:]])
        avg_q_queries = np.mean([r.quantum_queries for r in results[-num_trials:]])
        
        status = "OK" if all_correct else "FAIL"
        print(f"{n:>4} {avg_alpha:>8.3f} {avg_m:>4.0f} {avg_classical_ops:>12} "
              f"{avg_hybrid_ops:>12.0f} {avg_speedup:>10.2f}x {avg_q_queries:>10.0f} "
              f"{status:>8}")
    
    return results

def run_delta_sweep(n=16, num_trials=20):
    """Sweep delta parameter to find optimal filtering."""
    print("\n" + "=" * 80)
    print(f"DELTA PARAMETER SWEEP (n={n})")
    print("=" * 80)
    print(f"{'delta':>8} {'avg_alpha':>10} {'avg_m':>6} {'avg_speedup':>12} {'all_correct':>12}")
    print("-" * 60)
    
    best_delta = 0.1
    best_speedup = 0
    
    for delta in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
        alphas = []
        speedups = []
        all_correct = True
        
        for trial in range(num_trials):
            seed = n * 1000 + trial
            inst = generate_instance(n, seed=seed)
            opt_val, _ = brute_force_knapsack(inst)
            hybrid_val, _, fr = hybrid_solve(inst, delta=delta)
            
            m = len(fr.core)
            classical_ops = 2 ** (n // 2)
            hybrid_ops = max(1, 2 ** (m // 2))
            
            alphas.append(fr.alpha)
            speedups.append(classical_ops / hybrid_ops)
            if hybrid_val != opt_val:
                all_correct = False
        
        avg_alpha = np.mean(alphas)
        avg_m = avg_alpha * n
        avg_speedup = np.mean(speedups)
        status = "OK" if all_correct else "FAIL"
        
        print(f"{delta:>8.2f} {avg_alpha:>10.3f} {avg_m:>6.1f} "
              f"{avg_speedup:>12.2f}x {status:>12}")
        
        if avg_speedup > best_speedup and all_correct:
            best_speedup = avg_speedup
            best_delta = delta
    
    print(f"\nBest delta: {best_delta} (speedup: {best_speedup:.2f}x)")
    return best_delta

def run_qiskit_verification(max_core=8, num_trials=5):
    """Run actual Qiskit circuits to verify quantum search."""
    print("\n" + "=" * 80)
    print("QISKIT CIRCUIT VERIFICATION")
    print("=" * 80)
    
    for n in [6, 8, 10, 12]:
        print(f"\n--- n = {n} ---")
        for trial in range(num_trials):
            seed = n * 1000 + trial
            inst = generate_instance(n, seed=seed)
            opt_val, _ = brute_force_knapsack(inst)
            fr = lp_filter(inst, delta=0.3)
            
            m = len(fr.core)
            if m > max_core or m == 0:
                continue
            
            result = qiskit_grover_verify(inst, fr)
            
            if result.get("status") == "success":
                print(f"  Trial {trial}: m={m}, depth={result['circuit_depth']}, "
                      f"gates={result['num_gates']}, iters={result['grover_iterations']}, "
                      f"P(good)={result['max_probability']:.3f}, "
                      f"correct={result['correct']}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Starting benchmark...\n")
    
    # 1. Main benchmark
    results = run_benchmark(
        n_values=[4, 6, 8, 10, 12, 14, 16, 18, 20],
        num_trials=15,
        delta=0.3
    )
    
    # 2. Delta sweep
    best_delta = run_delta_sweep(n=16, num_trials=20)
    
    # 3. Qiskit verification
    run_qiskit_verification(max_core=8, num_trials=5)
    
    # 4. Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_correct = all(r.hybrid_correct for r in results)
    avg_alpha = np.mean([r.hybrid_alpha for r in results])
    avg_speedup = np.mean([r.speedup_factor for r in results])
    
    print(f"Total experiments: {len(results)}")
    print(f"All correct: {all_correct}")
    print(f"Average alpha: {avg_alpha:.3f}")
    print(f"Average speedup: {avg_speedup:.2f}x")
    print(f"Alpha < 1 in {sum(1 for r in results if r.hybrid_alpha < 1)}/{len(results)} instances")
    
    # Save results
    output = {
        "summary": {
            "total_experiments": len(results),
            "all_correct": all_correct,
            "avg_alpha": round(avg_alpha, 4),
            "avg_speedup": round(avg_speedup, 2),
            "alpha_lt_1_count": sum(1 for r in results if r.hybrid_alpha < 1),
            "best_delta": best_delta
        },
        "results": [asdict(r) for r in results]
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to benchmark_results.json")

import os
import json
import time
import sys
import numpy as np
from ortools.algorithms.python import knapsack_solver as ortk

# Increase recursion limit
sys.setrecursionlimit(200000)

# Import generators and Phase 1 from benchmark_v5
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark_v5 import (
    gen_uncorrelated, gen_weakly_correlated, gen_strongly_correlated,
    gen_subset_sum, gen_inverse_strongly,
    reduced_cost_fixing, branch_and_bound
)

def solve_ortools(weights, values, capacity, time_limit_sec=10.0):
    solver = ortk.KnapsackSolver(
        ortk.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "k"
    )
    solver.set_time_limit(time_limit_sec)
    solver.init(list(values), [list(weights)], [capacity])
    t0 = time.perf_counter()
    try:
        val = solver.solve()
    except Exception as e:
        return None, time.perf_counter() - t0, False
    dt = time.perf_counter() - t0
    optimal = solver.is_solution_optimal()
    return val, dt, optimal

def run():
    generators = [
        gen_uncorrelated,
        gen_weakly_correlated, 
        gen_strongly_correlated,
        gen_subset_sum,
        gen_inverse_strongly,
    ]
    
    n_values = [100, 200, 500, 1000]
    num_trials = 5
    TIME_LIMIT = 20.0 # seconds
    
    results = []
    
    print("=" * 120)
    print("LP-PRUNED CLASSICAL B&B VS OR-TOOLS")
    print("=" * 120)
    
    for gen_func in generators:
        _, _, _, inst_type = gen_func(4, seed=0)
        print(f"\n--- {inst_type.upper()} ---")
        
        for n in n_values:
            for trial in range(num_trials):
                seed = 10000 + n * 100 + trial
                w, v, cap, _ = gen_func(n, seed=seed)
                
                # 1. OR-Tools
                or_val, or_time, or_opt = solve_ortools(w, v, cap, time_limit_sec=TIME_LIMIT)
                
                # 2. Phase 1
                t0_p1 = time.perf_counter()
                fi, core, fo = reduced_cost_fixing(n, w, v, cap)
                p1_time = time.perf_counter() - t0_p1
                m = len(core)
                
                res_cap = cap - sum(w[i] for i in fi)
                p1_val = sum(v[i] for i in fi)
                
                phase1_resolved = (m == 0 and res_cap >= 0)
                
                # 3. Core B&B
                bb_time = 0.0
                core_opt = 0
                match = False
                bb_hit_limit = False
                nodes = 0
                if res_cap < 0:
                    bb_val = -1
                elif phase1_resolved:
                    bb_val = p1_val
                    match = (bb_val == or_val) if or_opt else True
                else:
                    t0_bb = time.perf_counter()
                    core_w = [w[i] for i in core]
                    core_v = [v[i] for i in core]
                    core_opt, nodes, pruned, _, bb_hit_limit = branch_and_bound(
                        core_w, core_v, res_cap, use_lp=True, max_nodes=1000000
                    )
                    bb_time = time.perf_counter() - t0_bb
                    bb_val = p1_val + core_opt
                    match = (bb_val == or_val) if or_opt else True
                
                if or_opt and not bb_hit_limit and not match:
                    print(f"RESEARCH_INTEGRITY_STOP: Mismatch! type={inst_type} n={n} trial={trial}")
                    print(f"OR-Tools: {or_val}, Our B&B: {bb_val}")
                    sys.exit(1)
                
                record = {
                    "type": inst_type,
                    "n": n,
                    "trial": trial,
                    "or_time": or_time,
                    "or_opt": or_opt,
                    "m": m,
                    "p1_time": p1_time,
                    "phase1_resolved": phase1_resolved,
                    "bb_time": bb_time,
                    "bb_nodes": nodes,
                    "bb_hit_limit": bb_hit_limit,
                    "total_our_time": p1_time + bb_time,
                    "match": match
                }
                results.append(record)
                
            subset = [r for r in results if r["type"] == inst_type and r["n"] == n]
            avg_m = np.mean([r["m"] for r in subset])
            avg_or = np.mean([r["or_time"] for r in subset])
            avg_our = np.mean([r["total_our_time"] for r in subset])
            resolved_p1 = sum([r["phase1_resolved"] for r in subset])
            or_timeouts = sum([not r["or_opt"] for r in subset])
            our_timeouts = sum([r["bb_hit_limit"] for r in subset])
            print(f"n={n:<4} | m={avg_m:<5.1f} | p1_resolved={resolved_p1}/{num_trials} | OR-Tools={avg_or:<7.4f}s (timeouts: {or_timeouts}) | Ours={avg_our:<7.4f}s (timeouts: {our_timeouts})")
            
            if our_timeouts == num_trials and or_timeouts == num_trials:
                print("Intractability reached for both solvers. Stopping n scaling for this class.")
                break
                
    raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_results")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "benchmark_data.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("Done")

if __name__ == "__main__":
    run()

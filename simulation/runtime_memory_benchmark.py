import time
import tracemalloc
import numpy as np
import scipy.stats as stats
import json

from benchmark_v5 import (
    gen_uncorrelated, gen_weakly_correlated, gen_strongly_correlated, 
    gen_subset_sum, gen_inverse_strongly,
    reduced_cost_fixing, branch_and_bound
)
from quantum_backtracking import quantum_bb_optimize

def run_classical_bb(weights, values, capacity):
    # Full classical B&B with LP bound but NO reduced cost fixing
    branch_and_bound(weights, values, capacity, use_lp=True, max_nodes=5000000)

def run_lp_pruned_bb(weights, values, capacity):
    # LP pruning
    fixed_one, core, fixed_zero = reduced_cost_fixing(len(weights), weights, values, capacity)
    if not core:
        return
    core_w = [weights[i] for i in core]
    core_v = [values[i] for i in core]
    core_c = capacity - sum(weights[i] for i in fixed_one)
    if core_c < 0:
        return
    branch_and_bound(core_w, core_v, core_c, use_lp=True, max_nodes=5000000)

def run_hybrid_quantum(weights, values, capacity):
    # LP pruning
    fixed_one, core, fixed_zero = reduced_cost_fixing(len(weights), weights, values, capacity)
    if not core:
        return True
    core_w = [weights[i] for i in core]
    core_v = [values[i] for i in core]
    core_c = capacity - sum(weights[i] for i in fixed_one)
    if core_c < 0:
        return True
    
    # Hybrid Quantum Walk (faithful simulation)
    # cap max_nodes to 20000
    res = quantum_bb_optimize(core_w, core_v, core_c, constant=1.0, K=11, max_nodes=20000)
    if res is None:
        return False  # SKIPPED_TREE_CAP
    return True

def main():
    generators = {
        "Uncorrelated": gen_uncorrelated,
        "Weakly correlated": gen_weakly_correlated,
        "Strongly correlated": gen_strongly_correlated,
        "Subset-sum": gen_subset_sum,
        "Inverse strongly": gen_inverse_strongly
    }
    
    ns = [12, 14, 16, 18, 20]
    num_seeds = 20
    timed_reps = 5
    mem_reps = 3
    
    results = []

    print("Starting benchmark...")
    
    for class_name, gen_func in generators.items():
        print(f"\\n--- {class_name} ---")
        for n in ns:
            for seed in range(num_seeds):
                w, v, cap, _ = gen_func(n, seed=seed * 1337 + n)
                
                # --- Method 1: Classical B&B ---
                run_classical_bb(w, v, cap)  # Warmup
                runtimes = []
                for _ in range(timed_reps):
                    t0 = time.perf_counter_ns()
                    run_classical_bb(w, v, cap)
                    t1 = time.perf_counter_ns()
                    runtimes.append(t1 - t0)
                
                peak_mems = []
                for _ in range(mem_reps):
                    tracemalloc.start()
                    run_classical_bb(w, v, cap)
                    current, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    peak_mems.append(peak)
                
                results.append({
                    "method": "Classical B&B", "class": class_name, "n": n, "seed": seed,
                    "runtimes_ns": runtimes, "peak_mem_bytes": peak_mems
                })

                # --- Method 2: LP-pruned B&B ---
                run_lp_pruned_bb(w, v, cap)  # Warmup
                runtimes = []
                for _ in range(timed_reps):
                    t0 = time.perf_counter_ns()
                    run_lp_pruned_bb(w, v, cap)
                    t1 = time.perf_counter_ns()
                    runtimes.append(t1 - t0)
                
                peak_mems = []
                for _ in range(mem_reps):
                    tracemalloc.start()
                    run_lp_pruned_bb(w, v, cap)
                    current, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    peak_mems.append(peak)
                    
                results.append({
                    "method": "LP-pruned B&B", "class": class_name, "n": n, "seed": seed,
                    "runtimes_ns": runtimes, "peak_mem_bytes": peak_mems
                })
                
                # --- Method 3: Hybrid quantum simulation ---
                success = run_hybrid_quantum(w, v, cap)  # Warmup
                if success:
                    runtimes = []
                    for _ in range(timed_reps):
                        t0 = time.perf_counter_ns()
                        run_hybrid_quantum(w, v, cap)
                        t1 = time.perf_counter_ns()
                        runtimes.append(t1 - t0)
                        
                    peak_mems = []
                    for _ in range(mem_reps):
                        tracemalloc.start()
                        run_hybrid_quantum(w, v, cap)
                        current, peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                        peak_mems.append(peak)
                        
                    results.append({
                        "method": "Hybrid quantum simulation", "class": class_name, "n": n, "seed": seed,
                        "runtimes_ns": runtimes, "peak_mem_bytes": peak_mems
                    })
                else:
                    results.append({
                        "method": "Hybrid quantum simulation", "class": class_name, "n": n, "seed": seed,
                        "status": "SKIPPED_TREE_CAP"
                    })
            
            print(f"Finished n={n}")
            
    with open('runtime_memory_raw.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Data collected. Fitting models...")

    # Data analysis
    def get_data(method, class_name):
        points = []
        for r in results:
            if r["method"] == method and r["class"] == class_name and r.get("status") != "SKIPPED_TREE_CAP":
                # using median across reps for the representative time per instance
                rep_med_time = np.median(r["runtimes_ns"])
                rep_med_mem = np.median(r["peak_mem_bytes"])
                points.append((r["n"], rep_med_time, rep_med_mem))
        return points
        
    print("| Method | Class | Median runtime | IQR | Peak memory | Scaling fit |")
    print("| --- | --- | --- | --- | --- | --- |")
    
    for method in ["Classical B&B", "LP-pruned B&B", "Hybrid quantum simulation"]:
        for class_name in generators.keys():
            data = get_data(method, class_name)
            if not data:
                continue
                
            n_vals = np.array([x[0] for x in data])
            t_vals = np.array([x[1] for x in data]) / 1e6  # convert to ms
            mem_vals = np.array([x[2] for x in data]) / 1024  # convert to KB
            
            med_t = np.median(t_vals)
            q75, q25 = np.percentile(t_vals, [75, 25])
            iqr = q75 - q25
            
            med_mem = np.median(mem_vals)
            
            # Fitting
            # Exp fit: log(t) = a + gamma * n
            # Pow fit: log(t) = a + b * log(n)
            log_t = np.log(t_vals)
            log_n = np.log(n_vals)
            
            # Exp
            slope_exp, int_exp, r_exp, p_exp, std_exp = stats.linregress(n_vals, log_t)
            r2_exp = r_exp**2
            
            # Pow
            slope_pow, int_pow, r_pow, p_pow, std_pow = stats.linregress(log_n, log_t)
            r2_pow = r_pow**2
            
            # Very basic AIC for OLS: n * log(RSS/n) + 2k
            # RSS = sum(residuals^2)
            pred_exp = int_exp + slope_exp * n_vals
            rss_exp = np.sum((log_t - pred_exp)**2)
            aic_exp = len(n_vals) * np.log(max(1e-10, rss_exp / len(n_vals))) + 2 * 2
            
            pred_pow = int_pow + slope_pow * log_n
            rss_pow = np.sum((log_t - pred_pow)**2)
            aic_pow = len(n_vals) * np.log(max(1e-10, rss_pow / len(n_vals))) + 2 * 2
            
            if aic_exp < aic_pow:
                fit_str = f"Exp ($\\gamma={slope_exp:.2f}$, $R^2={r2_exp:.2f}$)"
            else:
                fit_str = f"Pow ($b={slope_pow:.2f}$, $R^2={r2_pow:.2f}$)"
                
            # If all times are essentially instantaneous/flat (e.g., uncorrelated LP pruned)
            if med_t < 0.1: 
                fit_str = "Constant"
                
            print(f"| {method} | {class_name} | {med_t:.2f} ms | {iqr:.2f} ms | {med_mem:.1f} KB | {fit_str} |")

if __name__ == "__main__":
    main()

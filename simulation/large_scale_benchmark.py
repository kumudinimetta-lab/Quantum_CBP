import numpy as np
import time
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

@dataclass
class KnapsackInstance:
    n: int
    weights: list
    values: list
    capacity: int

def generate_instance(n: int, inst_type: str, seed: int, R: int = 1000) -> KnapsackInstance:
    rng = np.random.RandomState(seed)
    
    if inst_type == "uncorrelated":
        weights = rng.randint(1, R + 1, size=n).tolist()
        values = rng.randint(1, R + 1, size=n).tolist()
    elif inst_type == "weakly-correlated":
        weights = rng.randint(1, R + 1, size=n).tolist()
        values = [max(1, w + rng.randint(-R//10, R//10 + 1)) for w in weights]
    elif inst_type == "strongly-correlated":
        weights = rng.randint(1, R + 1, size=n).tolist()
        values = [w + R//10 for w in weights]
    elif inst_type == "subset-sum":
        weights = rng.randint(1, R + 1, size=n).tolist()
        values = weights.copy()
    elif inst_type == "inverse-strongly-correlated":
        values = rng.randint(1, R + 1, size=n).tolist()
        weights = [v + R//10 for v in values]
    else:
        raise ValueError("Unknown type")
        
    capacity = int(0.5 * sum(weights))
    return KnapsackInstance(n=n, weights=weights, values=values, capacity=capacity)

def greedy_lower_bound(items, W):
    w_sum = 0
    v_sum = 0
    for w, v, orig_idx in items:
        if w_sum + w <= W:
            w_sum += w
            v_sum += v
    return v_sum

def dantzig_bound(items, W, force_in=None, force_out=None):
    w_sum = 0
    v_sum = 0
    forced_w = 0
    forced_v = 0
    
    if force_in is not None:
        forced_w += items[force_in][0]
        forced_v += items[force_in][1]
        if forced_w > W:
            return -1 # Infeasible
            
    w_sum += forced_w
    v_sum += forced_v
    
    for i, (w, v, orig_idx) in enumerate(items):
        if i == force_in or i == force_out:
            continue
        if w_sum + w <= W:
            w_sum += w
            v_sum += v
        else:
            rem = W - w_sum
            v_sum += v * (rem / w)
            break
            
    return v_sum

def lp_variable_fixing(inst: KnapsackInstance):
    n = inst.n
    items = [(inst.weights[i], inst.values[i], i) for i in range(n)]
    
    # Sort by efficiency
    items.sort(key=lambda x: x[1]/x[0], reverse=True)
    
    Z_lb = greedy_lower_bound(items, inst.capacity)
    
    # Find split item in standard LP
    w_sum = 0
    split_idx = -1
    for i, (w, v, idx) in enumerate(items):
        if w_sum + w > inst.capacity:
            split_idx = i
            break
        w_sum += w
        
    if split_idx == -1:
        return 0, 0, n, 0.0 # Everything fits
        
    fixed_in = 0
    fixed_out = 0
    core = 0
    
    for i in range(n):
        if i < split_idx:
            # Check if we can fix out an item that LP wants IN
            bound = dantzig_bound(items, inst.capacity, force_out=i)
            if bound < Z_lb:
                fixed_in += 1
            else:
                core += 1
        elif i > split_idx:
            # Check if we can fix in an item that LP wants OUT
            bound = dantzig_bound(items, inst.capacity, force_in=i)
            if bound < Z_lb:
                fixed_out += 1
            else:
                core += 1
        else:
            core += 1 # Split item is always core
            
    return fixed_in, fixed_out, core, core/n

def run_large_scale_benchmark():
    n_values = [100, 500, 1000, 5000, 10000]
    types = ["uncorrelated", "weakly-correlated", "strongly-correlated", "subset-sum", "inverse-strongly-correlated"]
    seeds = range(5) # 5 seeds per configuration
    
    results = []
    
    print("Starting large-scale Phase 1 benchmark...")
    
    for inst_type in types:
        for n in n_values:
            print(f"Testing {inst_type} for n={n}...")
            alphas = []
            cores = []
            times = []
            
            for seed in seeds:
                inst = generate_instance(n, inst_type, seed)
                
                t0 = time.time()
                f_in, f_out, core, alpha = lp_variable_fixing(inst)
                t1 = time.time()
                
                alphas.append(alpha)
                cores.append(core)
                times.append((t1 - t0) * 1000)
                
            results.append({
                "type": inst_type,
                "n": n,
                "avg_alpha": float(np.mean(alphas)),
                "std_alpha": float(np.std(alphas)),
                "avg_core": float(np.mean(cores)),
                "std_core": float(np.std(cores)),
                "avg_time_ms": float(np.mean(times))
            })
            
    # Save raw JSON
    os.makedirs('../paper/results', exist_ok=True)
    with open('../paper/results/large_scale_benchmark.json', 'w') as f:
        json.dump({"data": results}, f, indent=2)
        
    print("\nBenchmark complete! Generating plots...")
    
    # Generate Alpha plot
    plt.rcParams.update({'font.size': 12, 'figure.dpi': 300})
    sns.set_style("whitegrid")
    
    plt.figure(figsize=(10, 6))
    for inst_type in types:
        type_data = [r for r in results if r["type"] == inst_type]
        ns = [r["n"] for r in type_data]
        alphas = [r["avg_alpha"] for r in type_data]
        plt.plot(ns, alphas, marker='o', linewidth=2, label=inst_type.replace('-', ' ').title())
        
    plt.xscale('log')
    plt.xlabel('Number of Items ($n$)')
    plt.ylabel('Core Ratio ($\\alpha = m/n$)')
    plt.title('Asymptotic Filtering Effectiveness (Phase 1)')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    
    plot_path = '../paper/results/large_scale_alpha.pdf'
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    
    print(f"Saved results to ../paper/results/")

if __name__ == "__main__":
    run_large_scale_benchmark()

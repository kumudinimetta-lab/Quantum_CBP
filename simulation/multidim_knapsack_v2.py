import json
import math
import numpy as np
import os

def _efficiency_order_multidim(weights_d, values, capacities):
    n = len(values)
    d = len(capacities)
    eff = []
    for i in range(n):
        w_agg = max(weights_d[i][j] / max(capacities[j], 1e-12) for j in range(d))
        eff.append(values[i] / max(w_agg, 1e-12))
    return sorted(range(n), key=lambda i: eff[i], reverse=True)

def _lp_bound_multidim(cum_w, cum_v, capacities, item_indices, weights_d, values):
    d = len(capacities)
    if not item_indices:
        return cum_v
    bounds = []
    for j in range(d):
        rem_j = capacities[j] - cum_w[j]
        if rem_j < 0:
            return -math.inf
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
    return min(bounds)

def lp_fix_multidim(weights_d, values, capacities):
    n = len(values)
    d = len(capacities)
    order = _efficiency_order_multidim(weights_d, values, capacities)
    rem = list(capacities)
    z_lb = 0
    for i in order:
        if all(weights_d[i][j] <= rem[j] for j in range(d)):
            for j in range(d):
                rem[j] -= weights_d[i][j]
            z_lb += values[i]
    
    cum_w_all = [0.0] * d
    split_idx = -1
    for i in order:
        if all(cum_w_all[j] + weights_d[i][j] <= capacities[j] for j in range(d)):
            for j in range(d):
                cum_w_all[j] += weights_d[i][j]
        else:
            split_idx = i
            break
            
    F1, F0, core = [], [], []
    for i in order:
        remaining_excl = [x for x in order if x != i]
        eff_i = values[i] / max(max(weights_d[i][j] / max(capacities[j], 1e-12) for j in range(d)), 1e-12)
        eff_s = 0.0
        if split_idx >= 0:
            eff_s = values[split_idx] / max(max(weights_d[split_idx][j] / max(capacities[j], 1e-12) for j in range(d)), 1e-12)

        if eff_i > eff_s:
            z_excl = _lp_bound_multidim([0.0]*d, 0.0, capacities, remaining_excl, weights_d, values)
            if z_excl < z_lb:
                F1.append(i)
            else:
                core.append(i)
        else:
            cum_forced = list(weights_d[i])
            if all(cum_forced[j] <= capacities[j] for j in range(d)):
                z_forced = _lp_bound_multidim(cum_forced, values[i], capacities, remaining_excl, weights_d, values)
                if z_forced < z_lb:
                    F0.append(i)
                else:
                    core.append(i)
            else:
                F0.append(i)

    return F1, core, F0

def gen_strongly_correlated_multidim(n, d, seed, R=100, cap_ratio=0.5):
    """
    Extends the strongly correlated generator to d dimensions.
    Each item's weights are independent ~ U[1, R].
    The item's value is correlated with its AVERAGE weight across the d constraints:
    v_i = floor( (sum_{j=1}^d w_{ij}) / d ) + R/10
    """
    rng = np.random.RandomState(seed)
    weights_d = [[int(rng.randint(1, R + 1)) for _ in range(d)] for _ in range(n)]
    values = [int(sum(weights_d[i]) / d) + R // 10 for i in range(n)]
    capacities = [int(cap_ratio * sum(weights_d[i][j] for i in range(n))) for j in range(d)]
    return weights_d, values, capacities

def run():
    n = 24
    num_trials = 20
    results = []
    
    for d in [1, 2, 3, 4]:
        alphas = []
        for trial in range(num_trials):
            seed = n * 1000 + d * 100 + trial
            wd, v, caps = gen_strongly_correlated_multidim(n, d, seed)
            F1, core, F0 = lp_fix_multidim(wd, v, caps)
            alphas.append(len(core) / n)
        
        mean_alpha = np.mean(alphas)
        std_alpha = np.std(alphas)
        ci = 1.96 * std_alpha / math.sqrt(num_trials)
        print(f"d={d}: mean_alpha = {mean_alpha:.3f} ± {ci:.3f} (std: {std_alpha:.3f}) min/max: {min(alphas):.2f}/{max(alphas):.2f}")
        results.append({
            "d": d,
            "n_trials": num_trials,
            "mean_alpha": mean_alpha,
            "std_alpha": std_alpha,
            "ci_95": ci,
            "min_alpha": min(alphas),
            "max_alpha": max(alphas)
        })

    os.makedirs("multidim_knapsack/raw_results", exist_ok=True)
    with open("multidim_knapsack/raw_results/multidim_strongly_corr_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run()

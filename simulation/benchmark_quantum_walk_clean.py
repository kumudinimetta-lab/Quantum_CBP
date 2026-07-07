import json
import math
import time
import hashlib
import sys
import subprocess
import datetime
from pathlib import Path

import numpy as np

from benchmark_v5 import reduced_cost_fixing

from quantum_backtracking import (
    efficiency_order,
    quantum_bb_optimize,
    _classical_optimum,
)


def gen_uncorrelated(n, seed, R=50):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, size=n).tolist()
    v = rng.randint(1, R + 1, size=n).tolist()
    return w, v, int(0.5 * sum(w))


def gen_weakly_correlated(n, seed, R=50):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, size=n).tolist()
    v = [max(1, wi + rng.randint(-R // 10, R // 10 + 1)) for wi in w]
    return w, v, int(0.5 * sum(w))


def gen_strongly_correlated(n, seed, R=50):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, size=n).tolist()
    v = [wi + R // 10 for wi in w]
    return w, v, int(0.5 * sum(w))


def gen_subset_sum(n, seed, R=50):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R + 1, size=n).tolist()
    v = list(w)
    return w, v, int(0.5 * sum(w))


def gen_inverse_strongly(n, seed, R=50):
    rng = np.random.RandomState(seed)
    v = rng.randint(1, R + 1, size=n).tolist()
    w = [vi + R // 10 for vi in v]
    return w, v, int(0.5 * sum(w))


GENERATORS = {
    "uncorrelated": gen_uncorrelated,
    "weakly_correlated": gen_weakly_correlated,
    "strongly_correlated": gen_strongly_correlated,
    "subset_sum": gen_subset_sum,
    "inverse_strongly": gen_inverse_strongly,
}

CONFIG_N_VALUES = [8, 10, 12, 14, 16, 18]

# Smoke test parameters
TRIALS_SMOKE = 2
PE_CONSTANT = 2.0
K_REPEATS = 11
MAX_NODES = 20000

def get_git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "UNKNOWN"

def get_package_versions():
    try:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8').split('\n')
        return [r for r in reqs if r.startswith(('numpy', 'scipy'))]
    except Exception:
        return []

def get_script_sha256():
    with open(__file__, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def run_clean_benchmark():
    script_sha256 = get_script_sha256()
    git_hash = get_git_hash()
    pkg_versions = get_package_versions()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_filename = "quantum_walk_results_smoke.json"
    
    manifest = {
        "git_commit": git_hash,
        "script_sha256": script_sha256,
        "python_version": sys.version,
        "package_versions": pkg_versions,
        "timestamp": timestamp,
        "classes": list(GENERATORS.keys()),
        "n_values": CONFIG_N_VALUES,
        "seeds": [f"1000 * n + t (t=0..{TRIALS_SMOKE-1})"],
        "pe_constant": PE_CONSTANT,
        "K_repeats": K_REPEATS,
        "max_nodes": MAX_NODES,
        "output_filename": out_filename
    }

    print("=== MANIFEST ===")
    print(json.dumps(manifest, indent=2))
    
    results = []
    
    for name, gen in GENERATORS.items():
        for n in CONFIG_N_VALUES:
            for t in range(TRIALS_SMOKE):
                seed = 1000 * n + t
                w, v, cap = gen(n, seed=seed)
                
                record = {
                    "class": name,
                    "n": n,
                    "seed": seed
                }
                
                # Classical optimal for correctness checking
                opt = _classical_optimum(w, v, cap)
                
                fi, core, fo = reduced_cost_fixing(n, w, v, cap)
                res_cap = cap - sum(w[i] for i in fi)
                m = len(core)
                
                record["m"] = m
                
                if res_cap < 0:
                    record["status"] = "ASSERTION_FAILURE"
                    record["reason"] = "Negative residual capacity"
                    results.append(record)
                    continue
                    
                if m == 0:
                    record["status"] = "EMPTY_CORE"
                    results.append(record)
                    continue

                core_w = [w[i] for i in core]
                core_v = [v[i] for i in core]
                
                res = quantum_bb_optimize(core_w, core_v, res_cap, constant=PE_CONSTANT,
                                          K=K_REPEATS, max_nodes=MAX_NODES)
                                          
                if res is None:
                    record["status"] = "TREE_CAP"
                    results.append(record)
                    continue
                
                d_bound = m
                T_lp = res.max_tree
                hybrid_opt = sum(v[i] for i in fi) + res.optimal_value
                
                if d_bound > m or T_lp > (2**(m+1)) - 1 or hybrid_opt != opt:
                    record["status"] = "ASSERTION_FAILURE"
                    record["reason"] = f"d_bound={d_bound}, T_LP={T_lp}, max={(2**(m+1))-1}, opt={opt}, hybrid={hybrid_opt}"
                    results.append(record)
                    continue
                
                record["status"] = "COMPLETED"
                record["T_LP"] = T_lp
                record["d_bound"] = d_bound
                record["Q_d"] = res.montanaro_queries_decisive
                record["quantum_queries"] = res.quantum_queries_total
                record["correctness"] = True
                record["opt"] = opt
                
                results.append(record)

    out_data = {
        "manifest": manifest,
        "records": results
    }
    
    with open(out_filename, "w") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"\nSaved -> {out_filename}")

if __name__ == "__main__":
    run_clean_benchmark()

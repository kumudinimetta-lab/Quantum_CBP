import json
import math
import time
import sys
import datetime
from pathlib import Path

import numpy as np

from benchmark_v5 import reduced_cost_fixing

from quantum_backtracking import (
    Tree,
    efficiency_order,
    build_walk_operator,
    build_threshold_tree,
    _fejer_at_zero,
    _classical_optimum
)
from benchmark_quantum_walk_clean import GENERATORS, CONFIG_N_VALUES, get_git_hash, get_package_versions, get_script_sha256

# Smoke test parameters
TRIALS_SMOKE = 2
PE_CONSTANT = 2.0
K_REPEATS = 11
MAX_NODES = 2000

def run_spectral_benchmark():
    script_sha256 = get_script_sha256()
    git_hash = get_git_hash()
    pkg_versions = get_package_versions()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_filename = "quantum_walk_spectral_smoke.json"
    
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
        "max_nodes": MAX_NODES,
        "output_filename": out_filename
    }

    print("=== SPECTRAL MANIFEST ===")
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
                
                # Classical optimal
                opt = _classical_optimum(w, v, cap)
                
                # LP Core Pruning
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
                order = efficiency_order(core_w, core_v)
                
                tau_marked = opt - sum(v[i] for i in fi)
                tau_unmarked = tau_marked + 1
                
                for label, tau in [("marked", tau_marked), ("unmarked", tau_unmarked)]:
                    tree = build_threshold_tree(core_w, core_v, res_cap, tau, order, max_nodes=MAX_NODES)
                    if tree is None:
                        record_copy = dict(record)
                        record_copy["status"] = "TREE_CAP"
                        record_copy["case_type"] = label
                        results.append(record_copy)
                        continue
                        
                    T_LP = tree.size
                    record_copy = dict(record)
                    record_copy["T_LP"] = T_LP
                    record_copy["d_bound"] = m
                    record_copy["case_type"] = label
                    
                    if T_LP > MAX_NODES:
                        record_copy["status"] = "TREE_CAP"
                        results.append(record_copy)
                        continue
                        
                    if T_LP <= 1:
                        record_copy["status"] = "EMPTY_CORE"
                        results.append(record_copy)
                        continue

                    W = build_walk_operator(tree, m)
                    W_dense = W.toarray()
                    
                    try:
                        evals, evecs = np.linalg.eig(W_dense)
                    except np.linalg.LinAlgError:
                        record_copy["status"] = "NUMERICAL_FAILURE"
                        results.append(record_copy)
                        continue
                        
                    phases = np.angle(evals)
                    root_vec = np.zeros(T_LP)
                    root_vec[0] = 1.0
                    overlaps = np.abs(evecs.conj().T @ root_vec) ** 2
                    
                    is_marked = any(tree.marked)
                    record_copy["marked"] = is_marked
                    
                    if is_marked:
                        # Marked case: Check phase-zero overlap
                        w_0 = float(sum(overlaps[i] for i in range(T_LP) if abs(phases[i]) <= 1e-10))
                        record_copy["w_0"] = w_0
                        
                        s_theoretical = max(1, int(math.ceil(math.log2(PE_CONSTANT * math.sqrt(T_LP * m) + 1.0))))
                        p_accepts = {}
                        for s in [max(1, s_theoretical - 2), max(1, s_theoretical - 1), s_theoretical, s_theoretical + 1]:
                            p_acc = 0.0
                            for phi_k, w_k in zip(phases, overlaps):
                                if w_k < 1e-15:
                                    continue
                                p_acc += w_k * _fejer_at_zero(phi_k, s)
                            p_accepts[f"s{s-s_theoretical}"] = float(p_acc)
                        record_copy["p_accepts"] = p_accepts
                        record_copy["s_theoretical"] = s_theoretical
                        record_copy["status"] = "COMPLETED"
                    else:
                        # Unmarked case: Check cumulative low-phase weight
                        c_vals = [0.125, 0.25, 0.5, 1.0, 2.0]
                        mu_metrics = {}
                        for c in c_vals:
                            Phi = (2.0 * c) / math.sqrt(T_LP * m)
                            mu_val = float(sum(overlaps[i] for i in range(T_LP) if abs(phases[i]) <= Phi))
                            bound_val = (Phi ** 2 / 4.0) * T_LP * m
                            mu_metrics[f"c_{c}"] = {
                                "Phi": Phi,
                                "mu": mu_val,
                                "bound": bound_val,
                                "valid": mu_val <= bound_val
                            }
                        record_copy["mu_metrics"] = mu_metrics
                        
                        # Smallest accessible eigenphase (diagnostic only)
                        acc_phases = [abs(phases[i]) for i in range(T_LP) if overlaps[i] > 1e-10 and abs(phases[i]) > 1e-10]
                        record_copy["smallest_accessible_phase"] = float(min(acc_phases)) if acc_phases else None
                        
                        s_theoretical = max(1, int(math.ceil(math.log2(PE_CONSTANT * math.sqrt(T_LP * m) + 1.0))))
                        p_accepts = {}
                        for s in [max(1, s_theoretical - 2), max(1, s_theoretical - 1), s_theoretical, s_theoretical + 1]:
                            p_acc = 0.0
                            for phi_k, w_k in zip(phases, overlaps):
                                if w_k < 1e-15:
                                    continue
                                p_acc += w_k * _fejer_at_zero(phi_k, s)
                            p_accepts[f"s{s-s_theoretical}"] = float(p_acc)
                        record_copy["p_accepts"] = p_accepts
                        record_copy["s_theoretical"] = s_theoretical
                        record_copy["status"] = "COMPLETED"

                    results.append(record_copy)

    out_data = {
        "manifest": manifest,
        "records": results
    }
    
    with open(out_filename, "w") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"\nSaved -> {out_filename}")

if __name__ == "__main__":
    run_spectral_benchmark()

"""
IBM Quantum Hardware Experiment: LP-Pruned Quantum B&B Knapsack
================================================================
Runs the quantum oracle + amplitude amplification (Phase 2) on
real IBM quantum hardware for small core instances (3-4 items).

This validates that the quantum phase of our algorithm works on
actual quantum processors, not just simulation.
"""

import numpy as np
import json
import time
import sys
from datetime import datetime

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# ============================================================
# CONFIGURATION
# ============================================================
IBM_TOKEN = "TWijs-f4bzHyoIXNBjH2qBjBWWg2EmXDIbwYbq9SYpl8"
SHOTS = 8192
OPTIMIZATION_LEVEL = 3

# ============================================================
# SMALL CORE KNAPSACK INSTANCES FOR HARDWARE
# ============================================================
INSTANCES = [
    {
        "name": "Core-3A (Easy)",
        "weights": [2, 3, 4],
        "values":  [3, 4, 5],
        "capacity": 5,
        "description": "3-item core after LP fixing (uncorrelated)"
    },
    {
        "name": "Core-3B (Medium)",
        "weights": [3, 4, 5],
        "values":  [4, 5, 7],
        "capacity": 7,
        "description": "3-item core after LP fixing (weakly correlated)"
    },
    {
        "name": "Core-4A (Hard)",
        "weights": [2, 3, 4, 5],
        "values":  [3, 4, 5, 8],
        "capacity": 8,
        "description": "4-item core after LP fixing (strongly correlated)"
    },
    {
        "name": "Core-4B (Subset-Sum)",
        "weights": [3, 5, 7, 8],
        "values":  [3, 5, 7, 8],
        "capacity": 13,
        "description": "4-item core (subset-sum type, v_i = w_i)"
    },
    {
        "name": "Core-5A (Uncorrelated)",
        "weights": [2, 3, 4, 5, 6],
        "values":  [5, 4, 7, 3, 8],
        "capacity": 12,
        "description": "5-item core after LP fixing (uncorrelated)"
    },
    {
        "name": "Core-5B (Correlated)",
        "weights": [3, 5, 7, 9, 11],
        "values":  [4, 6, 8, 10, 12],
        "capacity": 18,
        "description": "5-item core after LP fixing (weakly correlated)"
    },
    {
        "name": "Core-6A (Hard)",
        "weights": [2, 3, 5, 7, 8, 10],
        "values":  [3, 5, 7, 9, 11, 13],
        "capacity": 20,
        "description": "6-item core after LP fixing (strongly correlated)"
    },
    {
        "name": "Core-6B (Subset-Sum)",
        "weights": [3, 5, 7, 8, 11, 13],
        "values":  [3, 5, 7, 8, 11, 13],
        "capacity": 24,
        "description": "6-item core (subset-sum type, v_i = w_i)"
    },
]

# ============================================================
# CLASSICAL GROUND TRUTH
# ============================================================
def solve_classical(weights, values, capacity):
    """Brute force optimal solution."""
    n = len(weights)
    best_val = 0
    best_mask = 0
    for mask in range(1 << n):
        w, v = 0, 0
        for i in range(n):
            if mask & (1 << i):
                w += weights[i]
                v += values[i]
        if w <= capacity and v > best_val:
            best_val = v
            best_mask = mask
    
    # Get all optimal states
    optimal_states = []
    for mask in range(1 << n):
        w, v = 0, 0
        for i in range(n):
            if mask & (1 << i):
                w += weights[i]
                v += values[i]
        if w <= capacity and v == best_val:
            # Binary string in Qiskit convention (big-endian: MSB first)
            state = format(mask, f'0{n}b')
            optimal_states.append(state)
    
    return best_val, best_mask, optimal_states

# ============================================================
# BUILD QUANTUM CIRCUIT
# ============================================================
def build_grover_circuit(weights, values, capacity, best_val):
    """
    Build Grover/amplitude amplification circuit for the knapsack oracle.
    Marks states that achieve the optimal value.
    """
    n = len(weights)
    N = 2**n
    
    # Count target states
    target_indices = []
    for i in range(N):
        w, v = 0, 0
        for j in range(n):
            if i & (1 << j):
                w += weights[j]
                v += values[j]
        if w <= capacity and v >= best_val:
            target_indices.append(i)
    
    t = len(target_indices)
    
    # Build oracle as diagonal matrix
    diagonal = np.ones(N)
    for idx in target_indices:
        diagonal[idx] = -1
    oracle_op = Operator(np.diag(diagonal))
    
    # Build diffuser
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))
    diffuser.h(n-1)
    diffuser.mcx(list(range(n-1)), n-1)
    diffuser.h(n-1)
    diffuser.x(range(n))
    diffuser.h(range(n))
    diff_op = Operator(diffuser)
    
    # Calculate optimal iterations
    iterations = max(1, int(np.floor((np.pi / 4) * np.sqrt(N / t))))
    
    # Build full circuit
    qc = QuantumCircuit(n)
    qc.h(range(n))  # Uniform superposition
    
    for _ in range(iterations):
        qc.append(oracle_op, range(n))
        qc.append(diff_op, range(n))
    
    # Add measurements
    qc.measure_all()
    
    return qc, iterations, t, target_indices

# ============================================================
# SIMULATOR BASELINE
# ============================================================
def run_simulator(weights, values, capacity, best_val):
    """Run on local simulator for comparison."""
    n = len(weights)
    N = 2**n
    
    # Build circuit WITHOUT measurements for statevector
    target_indices = []
    for i in range(N):
        w, v = 0, 0
        for j in range(n):
            if i & (1 << j):
                w += weights[j]
                v += values[j]
        if w <= capacity and v >= best_val:
            target_indices.append(i)
    
    t = len(target_indices)
    diagonal = np.ones(N)
    for idx in target_indices:
        diagonal[idx] = -1
    oracle_op = Operator(np.diag(diagonal))
    
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))
    diffuser.h(n-1)
    diffuser.mcx(list(range(n-1)), n-1)
    diffuser.h(n-1)
    diffuser.x(range(n))
    diffuser.h(range(n))
    diff_op = Operator(diffuser)
    
    iterations = max(1, int(np.floor((np.pi / 4) * np.sqrt(N / t))))
    
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iterations):
        qc.append(oracle_op, range(n))
        qc.append(diff_op, range(n))
    
    sv = Statevector(qc)
    probs = sv.probabilities_dict()
    
    # Calculate success probability
    success_prob = 0.0
    for idx in target_indices:
        # Qiskit probabilities_dict() keys are big-endian: key = format(idx, '0nb')
        # No reversal needed — idx directly maps to the state vector index
        state = format(idx, f'0{n}b')
        success_prob += probs.get(state, 0.0)
    
    return success_prob, probs, iterations

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("=" * 70)
    print(" IBM QUANTUM HARDWARE: KNAPSACK ORACLE EXPERIMENT")
    print(" LP-Pruned Quantum B&B - Phase 2 Validation")
    print(f" Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # ----- Step 1: Connect to IBM Quantum -----
    print("\n[1/5] Connecting to IBM Quantum...")
    try:
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform",
            token=IBM_TOKEN
        )
        print("  [OK] Connected successfully")
    except Exception as e:
        print(f"  [FAIL] Connection failed: {e}")
        sys.exit(1)
    
    # ----- Step 2: Select backend -----
    print("\n[2/5] Selecting quantum backend...")
    try:
        backends = service.backends(
            simulator=False,
            operational=True,
            min_num_qubits=4
        )
        print(f"  Available backends: {[b.name for b in backends]}")
        
        # Pick least busy
        backend = service.least_busy(
            simulator=False,
            operational=True,
            min_num_qubits=4
        )
        print(f"  [OK] Selected: {backend.name} ({backend.num_qubits} qubits)")
        backend_name = backend.name
    except Exception as e:
        print(f"  [FAIL] Backend selection failed: {e}")
        sys.exit(1)
    
    # ----- Step 3: Run simulator baselines -----
    print("\n[3/5] Running local simulator baselines...")
    all_results = []
    circuits_for_hw = []
    instance_meta = []
    
    for inst in INSTANCES:
        w, v, cap = inst["weights"], inst["values"], inst["capacity"]
        name = inst["name"]
        n = len(w)
        
        # Classical solution
        best_val, best_mask, optimal_states = solve_classical(w, v, cap)
        
        # Simulator
        sim_prob, sim_probs, iterations = run_simulator(w, v, cap, best_val)
        
        # Build hardware circuit
        qc, iters, t, target_indices = build_grover_circuit(w, v, cap, best_val)
        circuits_for_hw.append(qc)
        instance_meta.append({
            "name": name,
            "n": n,
            "optimal_value": best_val,
            "optimal_states": optimal_states,
            "target_count": t,
            "grover_iterations": iterations,
            "target_indices": target_indices,
            "sim_success_prob": sim_prob,
        })
        
        print(f"\n  {name} (n={n}):")
        print(f"    Items: w={w}, v={v}, cap={cap}")
        print(f"    Optimal value: {best_val}")
        print(f"    Optimal states: {optimal_states}")
        print(f"    Grover iterations: {iterations}")
        print(f"    Simulator success prob: {sim_prob*100:.1f}%")
    
    # ----- Step 4: Transpile and submit to hardware -----
    print(f"\n[4/5] Transpiling circuits for {backend_name}...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=OPTIMIZATION_LEVEL)
    
    transpiled_circuits = []
    for i, qc in enumerate(circuits_for_hw):
        tqc = pm.run(qc)
        transpiled_circuits.append(tqc)
        depth = tqc.depth()
        num_gates = tqc.count_ops()
        cx_count = sum(v for k, v in num_gates.items() if 'cx' in k or 'ecr' in k or 'cz' in k)
        instance_meta[i]["transpiled_depth"] = depth
        instance_meta[i]["two_qubit_gates"] = cx_count
        print(f"  {instance_meta[i]['name']}: depth={depth}, 2Q-gates={cx_count}")
    
    print(f"\n  Submitting {len(transpiled_circuits)} circuits to {backend_name} ({SHOTS} shots each)...")
    print("  [WAIT] This may take several minutes (queue wait + execution)...")
    
    try:
        sampler = SamplerV2(backend)
        
        # Submit all circuits as separate jobs for reliability
        jobs = []
        for i, tqc in enumerate(transpiled_circuits):
            job = sampler.run([tqc], shots=SHOTS)
            jobs.append(job)
            print(f"  -> Job {i+1}/{len(transpiled_circuits)} submitted: {job.job_id()}")
        
        # Wait for results
        print("\n  Waiting for hardware results...")
        hw_results = []
        for i, job in enumerate(jobs):
            print(f"  [WAIT] Waiting for job {i+1} ({instance_meta[i]['name']})...", end="", flush=True)
            result = job.result()
            hw_results.append(result)
            print(f" [OK] Done!")
        
    except Exception as e:
        print(f"\n  [FAIL] Hardware execution failed: {e}")
        print("  Saving simulator-only results...")
        save_results(all_results, instance_meta, backend_name, hw_failed=True)
        sys.exit(1)
    
    # ----- Step 5: Analyze results -----
    print("\n[5/5] Analyzing hardware results...")
    print("=" * 70)
    
    for i, (result, meta) in enumerate(zip(hw_results, instance_meta)):
        name = meta["name"]
        n = meta["n"]
        optimal_states = meta["optimal_states"]
        target_indices = meta["target_indices"]
        
        # Extract counts from the result
        pub_result = result[0]
        counts = pub_result.data.meas.get_counts()
        total_shots = sum(counts.values())
        
        # Calculate hardware success probability
        hw_success_shots = 0
        for state_str, count in counts.items():
            # Check if this measured state corresponds to an optimal solution
            # Qiskit returns states in the measurement register order
            idx = int(state_str, 2)
            if idx in target_indices:
                hw_success_shots += count
        
        hw_success_prob = hw_success_shots / total_shots
        sim_prob = meta["sim_success_prob"]
        
        # Get top measured states
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Find the most measured optimal state
        best_hw_state = None
        best_hw_count = 0
        for state_str, count in sorted_counts:
            idx = int(state_str, 2)
            if idx in target_indices:
                if count > best_hw_count:
                    best_hw_state = state_str
                    best_hw_count = count
        
        # Determine if correct solution was found
        found_optimal = hw_success_prob > 0
        
        # Check if optimal state is the TOP measured state
        top_state = sorted_counts[0][0]
        top_idx = int(top_state, 2)
        optimal_is_top = top_idx in target_indices
        
        print(f"\n{'-' * 70}")
        print(f"  Instance: {name} (n={n})")
        print(f"  Optimal value: {meta['optimal_value']}")
        print(f"  Grover iterations: {meta['grover_iterations']}")
        print(f"  Transpiled depth: {meta['transpiled_depth']}")
        print(f"  Two-qubit gates: {meta['two_qubit_gates']}")
        print(f"  --------------------------------------")
        print(f"  Simulator success prob:  {sim_prob*100:.1f}%")
        print(f"  Hardware success prob:   {hw_success_prob*100:.1f}%")
        print(f"  Noise penalty:           {(sim_prob - hw_success_prob)*100:+.1f}%")
        print(f"  Optimal found in top-1:  {'YES' if optimal_is_top else 'NO'}")
        print(f"  Optimal found at all:    {'YES' if found_optimal else 'NO'}")
        print(f"  Top 5 measured states:")
        for state_str, count in sorted_counts[:5]:
            idx = int(state_str, 2)
            prob = count / total_shots
            is_opt = "<< OPTIMAL" if idx in target_indices else ""
            # Decode to item selection
            items_selected = [j for j in range(n) if idx & (1 << j)]
            w_sum = sum(meta_w for j, meta_w in enumerate(INSTANCES[i]["weights"]) if j in items_selected)
            v_sum = sum(meta_v for j, meta_v in enumerate(INSTANCES[i]["values"]) if j in items_selected)
            feas = "Y" if w_sum <= INSTANCES[i]["capacity"] else "N"
            print(f"    |{state_str}>: {prob*100:5.1f}%  ({count:4d} shots)  "
                  f"items={items_selected} w={w_sum} v={v_sum} {feas} {is_opt}")
        
        meta["hw_success_prob"] = hw_success_prob
        meta["hw_optimal_is_top"] = optimal_is_top
        meta["hw_found_optimal"] = found_optimal
        meta["hw_counts"] = dict(sorted_counts[:10])
        meta["hw_noise_penalty"] = sim_prob - hw_success_prob
        meta["total_shots"] = total_shots
    
    # ----- Summary Table -----
    print(f"\n{'=' * 70}")
    print("  SUMMARY TABLE (for paper)")
    print(f"{'=' * 70}")
    print(f"  {'Instance':<22} {'n':>2} {'Iter':>4} {'Depth':>5} {'2Q':>4} "
          f"{'Sim%':>6} {'HW%':>6} {'Top-1':>5} {'Found':>5}")
    print(f"  {'-'*22} {'-'*2} {'-'*4} {'-'*5} {'-'*4} {'-'*6} {'-'*6} {'-'*5} {'-'*5}")
    
    for meta in instance_meta:
        print(f"  {meta['name']:<22} {meta['n']:>2} {meta['grover_iterations']:>4} "
              f"{meta['transpiled_depth']:>5} {meta['two_qubit_gates']:>4} "
              f"{meta['sim_success_prob']*100:>5.1f}% {meta['hw_success_prob']*100:>5.1f}% "
              f"{'Y' if meta['hw_optimal_is_top'] else 'N':>5} "
              f"{'Y' if meta['hw_found_optimal'] else 'N':>5}")
    
    # Save results
    save_results(instance_meta, backend_name)
    
    print(f"\n{'=' * 70}")
    print("  EXPERIMENT COMPLETE")
    print(f"  Backend: {backend_name}")
    print(f"  Shots per circuit: {SHOTS}")
    print(f"  Total circuits: {len(INSTANCES)}")
    print(f"{'=' * 70}")

def save_results(instance_meta, backend_name, hw_failed=False):
    """Save results to JSON for paper inclusion."""
    output = {
        "experiment": "IBM Quantum Hardware Validation",
        "timestamp": datetime.now().isoformat(),
        "backend": backend_name,
        "shots": SHOTS,
        "optimization_level": OPTIMIZATION_LEVEL,
        "hw_failed": hw_failed,
        "instances": []
    }
    
    for meta in instance_meta:
        inst_data = {
            "name": meta["name"],
            "n": meta["n"],
            "optimal_value": meta["optimal_value"],
            "optimal_states": meta["optimal_states"],
            "grover_iterations": meta["grover_iterations"],
            "sim_success_prob": float(meta["sim_success_prob"]),
        }
        if not hw_failed and "hw_success_prob" in meta:
            inst_data.update({
                "transpiled_depth": meta["transpiled_depth"],
                "two_qubit_gates": meta["two_qubit_gates"],
                "hw_success_prob": float(meta["hw_success_prob"]),
                "hw_optimal_is_top": meta["hw_optimal_is_top"],
                "hw_found_optimal": meta["hw_found_optimal"],
                "hw_noise_penalty": float(meta["hw_noise_penalty"]),
                "hw_top_counts": meta.get("hw_counts", {}),
                "total_shots": meta.get("total_shots", SHOTS),
            })
        output["instances"].append(inst_data)
    
    outfile = "ibm_hardware_results.json"
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {outfile}")


if __name__ == "__main__":
    main()

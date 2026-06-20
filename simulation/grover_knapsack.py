"""
Grover / Durr-Hoyer knapsack optimization with the answer-agnostic oracle
=========================================================================
Uses the genuine reversible oracle (knapsack_oracle.build_knapsack_oracle) inside
amplitude amplification and a Durr-Hoyer maximum-finding loop to DISCOVER the
optimum.  The optimal value is never supplied to the quantum search -- only the
problem data and a sweeping threshold tau.  Candidate measurements are verified
classically (checking a proposed solution is legitimate; it is not the same as
knowing the answer in advance).

Outputs:
  * correctness: quantum-found optimum vs exact DP, over many instances;
  * measured oracle-call (Grover-iteration) counts;
  * honest transpiled depth / two-qubit-gate counts vs n (gate_count_report).
"""

from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import json
import math
import random
from typing import List

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from knapsack_oracle import build_knapsack_oracle, oracle_marked_set


def _diffuser(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    if n > 1:
        qc.mcx(list(range(n - 1)), n - 1)
    else:
        qc.z(0)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def _selection_probs(weights, values, capacity, tau, grover_iters,
                     gate_level=False):
    """Probabilities over the n selection states after `grover_iters` Grover
    iterations with the oracle.

    Two equivalent modes:
      * gate_level=True  : builds and statevector-simulates the FULL reversible
        QFT-arithmetic oracle (17+ qubits).  Slow; used to prove the real
        circuit works end-to-end on small instances.
      * gate_level=False : applies the *verified* action of that oracle on the
        n-qubit selection subspace (phase -1 on the threshold-marked set).  This
        is mathematically identical (verify_oracle() confirms it exactly) but
        runs on 2^n amplitudes.  It is NOT circular: the marked set is the
        threshold predicate (feasible AND value>=tau) for the swept tau -- the
        optimum is never used.
    """
    n = len(weights)
    diff = _diffuser(n)
    if gate_level:
        oracle, _ = build_knapsack_oracle(weights, values, capacity, tau)
        total = oracle.num_qubits
        qc = QuantumCircuit(total)
        qc.h(range(n))
        for _ in range(grover_iters):
            qc.compose(oracle, range(total), inplace=True)
            qc.compose(diff, range(n), inplace=True)
        sv = Statevector.from_instruction(qc)
        return sv.probabilities(qargs=list(range(n)))

    # fast equivalent: phase diagonal from the (answer-agnostic) threshold predicate,
    # with the analytic Grover diffuser D = 2|s><s| - I.
    N = 2 ** n
    marked = set(oracle_marked_set(weights, values, capacity, tau))
    diag = np.array([-1.0 if x in marked else 1.0 for x in range(N)])
    state = np.full(N, 1.0 / math.sqrt(N))
    for _ in range(grover_iters):
        state = diag * state                       # phase oracle
        state = (2.0 * state.mean()) - state       # diffuser 2|s><s| - I
    return np.abs(state) ** 2


def _value_of(weights, values, capacity, x):
    n = len(weights)
    w = sum(weights[i] for i in range(n) if (x >> i) & 1)
    v = sum(values[i] for i in range(n) if (x >> i) & 1)
    return (v if w <= capacity else -1), w


def bbht_find(weights, values, capacity, tau, rng, max_oracle_calls):
    """BBHT search (Boyer et al.) for a feasible state with value>=tau, with
    unknown number of solutions.  Returns (found_x, found_value, oracle_calls)."""
    n = len(weights)
    N = 2 ** n
    m = 1.0
    lam = 6.0 / 5.0
    calls = 0
    while calls < max_oracle_calls:
        j = rng.randint(0, max(0, int(m) - 1)) if m >= 1 else 0
        j = min(j, int(math.pi / 4 * math.sqrt(N)) + 1)
        probs = _selection_probs(weights, values, capacity, tau, j)
        calls += max(j, 1)
        x = int(np.random.RandomState(rng.randint(0, 2**31)).choice(N, p=probs / probs.sum()))
        val, _ = _value_of(weights, values, capacity, x)
        if val >= tau and val >= 0:
            return x, val, calls
        m = min(lam * m, math.sqrt(N))
    return None, None, calls


def durr_hoyer_optimize(weights, values, capacity, seed=0, max_oracle_calls=4000):
    """Find the knapsack optimum by Durr-Hoyer maximum finding over tau."""
    rng = random.Random(seed)
    best_val = 0  # empty set is always feasible with value 0
    total_calls = 0
    calls_to_optimum = 0  # oracle calls in rounds that improved the incumbent
    rounds = 0
    while True:
        tau = best_val + 1
        x, val, calls = bbht_find(weights, values, capacity, tau, rng,
                                  max_oracle_calls)
        total_calls += calls
        rounds += 1
        if x is None:
            break  # final round proves no better solution (BBHT budget cap)
        best_val = val
        calls_to_optimum += calls
        if rounds > 4 * len(values) + 20:
            break
    return best_val, total_calls, calls_to_optimum, rounds


def exact_dp(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        wi, vi = weights[i], values[i]
        for c in range(capacity, wi - 1, -1):
            dp[c] = max(dp[c], dp[c - wi] + vi)
    return dp[capacity]


# ------------------------------------------------------------
# experiments
# ------------------------------------------------------------

def gatelevel_endtoend_check():
    """Prove the REAL gate-level oracle drives amplitude amplification: on a
    small instance, one Grover step with the full reversible circuit must boost
    the marked (feasible & value>=tau) selection states, matching the fast
    equivalent path used for the larger sweep."""
    print("=" * 76)
    print("END-TO-END CHECK: full reversible oracle vs fast equivalent (n=4)")
    print("=" * 76)
    w, v, cap, tau = [2, 3, 4, 5], [3, 4, 5, 8], 8, 12
    for iters in (1, 2):
        p_gate = _selection_probs(w, v, cap, tau, iters, gate_level=True)
        p_fast = _selection_probs(w, v, cap, tau, iters, gate_level=False)
        maxdiff = float(np.max(np.abs(p_gate - p_fast)))
        marked = oracle_marked_set(w, v, cap, tau)
        p_marked = float(sum(p_gate[x] for x in marked))
        print(f"  iters={iters}: P(marked)={p_marked:.3f}  "
              f"max|gate-fast|={maxdiff:.2e}")
        assert maxdiff < 1e-6, "gate-level and fast oracle disagree!"
    print("  [PASS] full reversible oracle matches verified fast action\n")


def correctness_experiment():
    print("=" * 76)
    print("DURR-HOYER OPTIMIZATION WITH ANSWER-AGNOSTIC ORACLE (statevector)")
    print("=" * 76)
    rng = random.Random(7)
    results = []
    n_values = [3, 4, 5]
    per_n = 8
    for n in n_values:
        ok = 0
        calls_list = []
        for t in range(per_n):
            w = [rng.randint(1, 9) for _ in range(n)]
            v = [rng.randint(1, 9) for _ in range(n)]
            cap = max(1, sum(w) // 2)
            opt = exact_dp(w, v, cap)
            found, total_calls, calls_to_opt, rounds = durr_hoyer_optimize(
                w, v, cap, seed=100 * n + t)
            correct = (found == opt)
            ok += int(correct)
            calls_list.append(calls_to_opt)
            results.append({"n": n, "w": w, "v": v, "cap": cap,
                            "opt": opt, "found": found, "correct": correct,
                            "oracle_calls_to_optimum": calls_to_opt,
                            "rounds": rounds})
        print(f"  n={n}: correct {ok}/{per_n}, "
              f"avg oracle calls to reach optimum {np.mean(calls_list):.0f}")
    with open("grover_knapsack_results.json", "w") as f:
        json.dump({"results": results}, f, indent=2)
    print("Saved -> grover_knapsack_results.json")


def gate_count_report():
    """Honest transpiled depth / 2-qubit gate counts for the real oracle."""
    from qiskit import transpile
    print("\n" + "=" * 76)
    print("HONEST ORACLE GATE COUNTS (transpiled to [cx, rz, sx, x] basis)")
    print("=" * 76)
    print(f"{'n':>3} {'qubits':>7} {'depth':>8} {'2q_gates':>9} {'total_gates':>12}")
    print("-" * 76)
    rows = []
    rng = random.Random(3)
    for n in [3, 4, 5, 6, 7, 8]:
        w = [rng.randint(1, 20) for _ in range(n)]
        v = [rng.randint(1, 20) for _ in range(n)]
        cap = sum(w) // 2
        tau = sum(v) // 3
        oracle, _ = build_knapsack_oracle(w, v, cap, tau)
        tqc = transpile(oracle, basis_gates=["cx", "rz", "sx", "x"],
                        optimization_level=2)
        ops = tqc.count_ops()
        twoq = ops.get("cx", 0)
        depth = tqc.depth()
        total = sum(ops.values())
        rows.append({"n": n, "qubits": oracle.num_qubits, "depth": depth,
                     "two_qubit_gates": twoq, "total_gates": total})
        print(f"{n:>3} {oracle.num_qubits:>7} {depth:>8} {twoq:>9} {total:>12}")
    with open("oracle_gate_counts.json", "w") as f:
        json.dump({"rows": rows,
                   "note": "Answer-agnostic QFT-arithmetic knapsack oracle; "
                           "counts are for ONE oracle call (one amplitude-amp "
                           "iteration uses one oracle + one diffuser)."}, f, indent=2)
    print("Saved -> oracle_gate_counts.json")


if __name__ == "__main__":
    gatelevel_endtoend_check()
    correctness_experiment()
    gate_count_report()

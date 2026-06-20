"""
Genuine reversible knapsack oracle (answer-agnostic), QFT/Draper construction
=============================================================================
The previous oracle (quantum_oracle_verification.py / run_ibm_hardware.py) built
a *diagonal* unitary by first solving the instance classically and hard-coding
the optimal value into the marked states.  That is circular: the circuit
"finds" an answer that was already computed and baked in.

This module builds a real, gate-level reversible circuit that COMPUTES the
predicate

        feasible(x)  AND  value(x) >= tau

internally, and flips the phase of the marked computational-basis states.  The
only classical inputs are the problem data (weights, values, capacity) and a
value threshold ``tau`` -- NOT the optimal solution.  ``tau`` is swept by an
outer Grover/Durr-Hoyer loop (grover_optimize.py), so the optimum is discovered
by the quantum search, not supplied to it.

Arithmetic uses in-place Draper (QFT) addition -- zero ancilla beyond the two
accumulator registers -- and uses two's-complement sign bits as the feasibility
and value flags:

    weight(x) <= W      <=>  (weight - (W+1)) < 0  <=>  sign bit == 1
    value(x)  >= tau    <=>  (value  -  tau)  >= 0 <=>  sign bit == 0

QRAQM-free, gate-model only.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFT


def _bits_for(x: int) -> int:
    return max(1, int(abs(x)).bit_length())


def _add_const_fourier(qc: QuantumCircuit, reg: Sequence, a: int, ctrl=None):
    """Add integer ``a`` (mod 2^b) into ``reg`` which is already in the Fourier
    basis (QFT applied, do_swaps=False).  reg[0] = LSB.  Optionally controlled
    on a single qubit ``ctrl``."""
    b = len(reg)
    a = int(a) % (2 ** b)
    for j in range(b):
        # QFT(do_swaps=False) reverses wire order, so reg[j] gets weight 2^(b-1-j)
        angle = 2.0 * math.pi * a / (2 ** (j + 1))
        if angle % (2.0 * math.pi) == 0.0:
            continue
        if ctrl is None:
            qc.p(angle, reg[j])
        else:
            qc.cp(angle, ctrl, reg[j])


def build_knapsack_oracle(weights: List[int], values: List[int],
                          capacity: int, tau: int) -> Tuple[QuantumCircuit, QuantumRegister]:
    """Phase oracle marking x with weight(x)<=capacity AND value(x)>=tau.

    Ancillae (the two accumulators) are uncomputed back to |0>.  Uses only the
    problem data and tau -- never the optimal solution.
    """
    n = len(weights)
    sum_w = int(sum(weights))
    sum_v = int(sum(values))

    bw = _bits_for(sum_w + capacity + 2) + 1   # +1 two's-complement sign bit
    bv = _bits_for(sum_v + max(tau, 0) + 2) + 1

    sel = QuantumRegister(n, "x")
    wreg = QuantumRegister(bw, "w")
    vreg = QuantumRegister(bv, "v")
    qc = QuantumCircuit(sel, wreg, vreg, name=f"knap_oracle(tau={tau})")

    qft_w = QFT(bw, do_swaps=False)
    qft_v = QFT(bv, do_swaps=False)

    # ---- accumulate weight, then subtract (capacity+1) ----
    qc.append(qft_w.to_gate(), list(wreg))
    for i in range(n):
        _add_const_fourier(qc, list(wreg), weights[i], ctrl=sel[i])
    _add_const_fourier(qc, list(wreg), -(capacity + 1))   # sign bit -> feasibility
    qc.append(qft_w.inverse().to_gate(), list(wreg))

    # ---- accumulate value, then subtract tau ----
    qc.append(qft_v.to_gate(), list(vreg))
    for i in range(n):
        _add_const_fourier(qc, list(vreg), values[i], ctrl=sel[i])
    _add_const_fourier(qc, list(vreg), -max(tau, 0))      # sign bit -> value flag
    qc.append(qft_v.inverse().to_gate(), list(vreg))

    # ---- phase flip iff feasible (w sign==1) AND good value (v sign==0) ----
    w_sign = wreg[bw - 1]
    v_sign = vreg[bv - 1]
    qc.x(v_sign)                 # v_sign==1 now means value>=tau
    qc.cz(w_sign, v_sign)        # phase -1 iff feasible AND good value
    qc.x(v_sign)

    # ---- uncompute (reverse arithmetic) ----
    qc.append(qft_v.to_gate(), list(vreg))
    _add_const_fourier(qc, list(vreg), +max(tau, 0))
    for i in range(n):
        _add_const_fourier(qc, list(vreg), -values[i], ctrl=sel[i])
    qc.append(qft_v.inverse().to_gate(), list(vreg))

    qc.append(qft_w.to_gate(), list(wreg))
    _add_const_fourier(qc, list(wreg), +(capacity + 1))
    for i in range(n):
        _add_const_fourier(qc, list(wreg), -weights[i], ctrl=sel[i])
    qc.append(qft_w.inverse().to_gate(), list(wreg))

    return qc, sel


def oracle_marked_set(weights, values, capacity, tau) -> List[int]:
    """Brute-force ground truth: which basis states the oracle should mark."""
    n = len(weights)
    marked = []
    for x in range(2 ** n):
        w = sum(weights[i] for i in range(n) if (x >> i) & 1)
        v = sum(values[i] for i in range(n) if (x >> i) & 1)
        if w <= capacity and v >= tau:
            marked.append(x)
    return marked


def verify_oracle(weights, values, capacity, tau, atol=1e-6) -> bool:
    """Statevector check: oracle applies phase -1 exactly to the marked
    selection states (with ancillae returning to |0>)."""
    from qiskit.quantum_info import Statevector

    qc, sel = build_knapsack_oracle(weights, values, capacity, tau)
    n = len(weights)
    total = qc.num_qubits
    # uniform superposition over selection qubits only; ancillae stay |0>
    pre = QuantumCircuit(total)
    for q in range(n):
        pre.h(q)
    full = pre.compose(qc)
    sv = Statevector.from_instruction(full).data

    marked = set(oracle_marked_set(weights, values, capacity, tau))
    amp = 1.0 / math.sqrt(2 ** n)
    ok = True
    for x in range(2 ** n):
        # ancillae are qubits n..total-1 == 0; index into statevector is just x
        expected = -amp if x in marked else amp
        got = sv[x]
        if abs(got - expected) > atol:
            ok = False
            break
    # also confirm no leakage into ancilla!=0 subspace
    leak = float(np.sum(np.abs(sv[2 ** n:]) ** 2)) if total > n else 0.0
    return ok and leak < atol


if __name__ == "__main__":
    tests = [
        ([2, 3, 4, 5], [3, 4, 5, 8], 8),
        ([3, 5, 7, 8], [3, 5, 7, 8], 13),
        ([2, 3, 4, 5, 6], [5, 4, 7, 3, 8], 12),
    ]
    print("Verifying answer-agnostic oracle against brute-force marked sets:")
    for w, v, cap in tests:
        sum_v = sum(v)
        all_ok = True
        for tau in range(0, sum_v + 1):
            if not verify_oracle(w, v, cap, tau):
                all_ok = False
                print(f"  FAIL: w={w} v={v} W={cap} tau={tau}")
                break
        qc, sel = build_knapsack_oracle(w, v, cap, sum_v // 2)
        print(f"  w={w} v={v} W={cap}: all tau verified={all_ok}, "
              f"oracle qubits={qc.num_qubits}")

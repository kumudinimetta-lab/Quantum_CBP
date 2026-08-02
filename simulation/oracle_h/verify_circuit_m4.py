import math
import sys
import os
import random
import numpy as np

from qiskit import transpile
from qiskit import QuantumCircuit, QuantumRegister
import qiskit
from gate_builder import get_thapliyal_div, get_vbe_mul, get_draper_add, get_compare_le
from simulate_circuit import GateLevelSimulator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark_v5 import (
    gen_uncorrelated, gen_weakly_correlated, 
    gen_strongly_correlated, gen_subset_sum, gen_inverse_strongly
)

def build_full_circuit(W_max, V_max, Z_LB):
    k = math.ceil(2 * math.log2(W_max))
    sz_v = math.ceil(math.log2(V_max + 1)) + k
    sz_w = sz_v
    sz_e = sz_v
    sz_rem = sz_v
    sz_Wres = math.ceil(math.log2(W_max + 1))
    sz_frac = sz_Wres + sz_e
    sz_Vint = math.ceil(math.log2(V_max + 2)) + k
    
    q_v = QuantumRegister(sz_v, 'v_s_scaled')
    q_w = QuantumRegister(sz_w, 'w_s')
    q_e = QuantumRegister(sz_e, 'e_s')
    q_rem = QuantumRegister(sz_rem, 'rem')
    q_sign_rem = QuantumRegister(1, 'sign_rem')
    q_sign_w = QuantumRegister(1, 'sign_w')
    q_Wres = QuantumRegister(sz_Wres, 'W_res')
    q_frac = QuantumRegister(sz_frac, 'frac_val')
    q_Vint = QuantumRegister(sz_Vint, 'V_int_scaled')
    q_cmp = QuantumRegister(1, 'cmp_flag')
    
    qc = QuantumCircuit(q_v, q_w, q_e, q_rem, q_sign_rem, q_sign_w, q_Wres, q_frac, q_Vint, q_cmp)
    
    # 0. Copy v_s_scaled to e_s (out of place division)
    for i in range(sz_v):
        qc.cx(q_v[i], q_e[i])
        
    # 1. Div
    div = get_thapliyal_div(sz_v)
    qc.append(div, q_e[:] + q_w[:] + q_rem[:] + q_sign_rem[:] + q_sign_w[:])
    
    # 2. Mul (frac_val = W_res * e_s)
    mul = get_vbe_mul(sz_Wres, sz_e)
    qc.append(mul, q_Wres[:] + q_e[:] + q_frac[:])
    
    # 3. Add (V_int_scaled += frac_val)
    adder = get_draper_add(sz_Vint)
    frac_bits = q_frac[:]
    if len(frac_bits) < sz_Vint:
        pad = QuantumRegister(sz_Vint - len(frac_bits), 'pad_frac')
        qc.add_register(pad)
        frac_bits += pad[:]
    elif len(frac_bits) > sz_Vint:
        frac_bits = frac_bits[:sz_Vint]
        
    qc.append(adder, frac_bits + q_Vint[:])
    
    # 4. Compare
    T = math.floor(Z_LB * (2**k) - (2**k) / W_max)
    cmp = get_compare_le(sz_Vint, T)
    num_anc = cmp.num_ancillas
    global stored_cmp_anc
    stored_cmp_anc = num_anc
    if num_anc > 0:
        anc = QuantumRegister(num_anc, 'cmp_anc')
        qc.add_register(anc)
        qc.append(cmp, q_Vint[:] + q_cmp[:] + anc[:])
    else:
        qc.append(cmp, q_Vint[:] + q_cmp[:])
        
    return qc, {
        'q_v': q_v, 'q_w': q_w, 'q_Wres': q_Wres, 'q_Vint': q_Vint, 
        'q_cmp': q_cmp, 'q_e': q_e, 'q_frac': q_frac, 'q_rem': q_rem
    }

def verify_instance(sim, tqc, regs, k, W_max, Z_LB, v_s, w_s, W_res, V_int):
    v_s_scaled = v_s * (2**k)
    V_int_scaled = V_int * (2**k)
    
    # Check bounds
    assert v_s_scaled < (1 << regs['q_v'].size)
    assert w_s < (1 << regs['q_w'].size)
    assert W_res < (1 << regs['q_Wres'].size)
    assert V_int_scaled < (1 << regs['q_Vint'].size)
    
    # Set input state
    bitstring = ['0'] * tqc.num_qubits
    
    def set_val(qreg, val):
        for i in range(qreg.size):
            if (val >> i) & 1:
                bitstring[tqc.find_bit(qreg[i]).index] = '1'
                
    set_val(regs['q_v'], v_s_scaled)
    set_val(regs['q_w'], w_s)
    set_val(regs['q_Wres'], W_res)
    set_val(regs['q_Vint'], V_int_scaled)
    
    sim.set_input(''.join(reversed(bitstring))) # sim expects string like '101' where index 0 is rightmost?
    # Wait, my set_input loops reversed(bitstring). If string is '100', bit 0 is '0', bit 1 is '0', bit 2 is '1'.
    # This means bitstring[idx] = '1' gives correct alignment if we pass the string such that bitstring[-1-idx] is the bit.
    
    # Let's adjust set_input directly:
    sim.bits.fill(False)
    sim.phases.fill(0.0)
    sim.is_fourier.fill(False)
    for i in range(regs['q_v'].size):
        if (v_s_scaled >> i) & 1: sim.bits[tqc.find_bit(regs['q_v'][i]).index] = True
    for i in range(regs['q_w'].size):
        if (w_s >> i) & 1: sim.bits[tqc.find_bit(regs['q_w'][i]).index] = True
    for i in range(regs['q_Wres'].size):
        if (W_res >> i) & 1: sim.bits[tqc.find_bit(regs['q_Wres'][i]).index] = True
    for i in range(regs['q_Vint'].size):
        if (V_int_scaled >> i) & 1: sim.bits[tqc.find_bit(regs['q_Vint'][i]).index] = True
        
    sim.run(tqc)
    
    # Read output
    cmp_flag_idx = tqc.find_bit(regs['q_cmp'][0]).index
    sim_flag = sim.bits[cmp_flag_idx]
    
    # Exact math
    T = math.floor(Z_LB * (2**k) - (2**k) / W_max)
    exact_e = v_s_scaled // w_s
    exact_frac = W_res * exact_e
    exact_Vint = V_int_scaled + exact_frac
    exact_flag = exact_Vint <= T
    
    return sim_flag == exact_flag, sim_flag, exact_flag, exact_e

def run_test():
    W_max, V_max, Z_LB = 15, 15, 10
    k = math.ceil(2 * math.log2(W_max))
    
    print("Building full m=4 circuit...")
    qc, regs = build_full_circuit(W_max, V_max, Z_LB)
    
    print("Decomposing...")
    tqc = qc.copy()
    basis = {'x', 'cx', 'ccx', 'swap', 'h', 'cp', 'p', 'ccp', 'mcx', 'mcx_gray'}
    while True:
        to_decompose = [g.operation.name for g in tqc.data if g.operation.name not in basis]
        if not to_decompose:
            break
        tqc = tqc.decompose(gates_to_decompose=list(set(to_decompose)))
    
    # We might have mcx or mcx_gray left. Let's decompose those too if they exist.
    while True:
        to_decompose = [g.operation.name for g in tqc.data if g.operation.name not in {'x', 'cx', 'ccx', 'swap', 'h', 'cp', 'p', 'ccp'}]
        if not to_decompose:
            break
        tqc = tqc.decompose(gates_to_decompose=list(set(to_decompose)))
    
    print(f"Synthesized Circuit: {tqc.num_qubits} qubits, {sum(dict(tqc.count_ops()).values())} gates.")
    print(f"Gate counts: {dict(tqc.count_ops())}")
    
    # Get depth and T-count. In our basis, CCX and CCP have T gates. 
    # Let's count CCX and CCP as 7 T gates for a rough estimate, or just report raw CCX.
    ops = dict(tqc.count_ops())
    t_count = (ops.get('ccx', 0) + ops.get('ccp', 0)) * 7 
    depth = tqc.depth()
    print(f"MEASURED STATS (m=4): Qubits = {tqc.num_qubits}, Gates = {sum(ops.values())}, Depth = {depth}, Est. T-count = {t_count}")
    
    sim = GateLevelSimulator(tqc.num_qubits)
    
    # 1. Fault Injection Test
    print("\n--- INJECTED FAULT TEST ---")
    tqc_faulty = tqc.copy()
    # Inject a fault: flip an X gate to corrupt the division/multiplication
    # We find an existing X gate and duplicate it at index 50
    x_inst = next(inst for inst in tqc.data if inst.operation.name == 'x')
    tqc_faulty.data.insert(50, x_inst)
    sim_faulty = GateLevelSimulator(tqc_faulty.num_qubits)
    
    # Run exact math values
    v_s_test, w_s_test, W_res_test, V_int_test = 10, 15, 12, 2
    
    match_faulty, s_f, e_f, _ = verify_instance(sim_faulty, tqc_faulty, regs, k, W_max, Z_LB, v_s_test, w_s_test, W_res_test, V_int_test)
    match_clean, s_c, e_c, _ = verify_instance(sim, tqc, regs, k, W_max, Z_LB, v_s_test, w_s_test, W_res_test, V_int_test)
    
    print(f"clean-sim={s_c}, clean-exact={e_c}, faulted-sim={s_f}, faulted-exact={e_f}")
    print(f"Comparator Ancillas: {stored_cmp_anc}")
    
    # Calculate explicit base registers
    base_qubits = sum(r.size for r in [regs['q_v'], regs['q_w'], regs['q_e'], regs['q_rem'], qc.qregs[4], qc.qregs[5], regs['q_Wres'], regs['q_frac'], regs['q_Vint'], regs['q_cmp']])
    print(f"Base Register Qubits: {base_qubits}")
    print(f"Total Circuit Qubits: {tqc.num_qubits}")
    
    print("\n--- SAMPLING BENCHMARK INSTANCES ---")
    generators = [gen_uncorrelated, gen_weakly_correlated, gen_strongly_correlated, gen_subset_sum, gen_inverse_strongly]
    mismatches = 0
    total = 0
    
    for gen_func in generators:
        for trial in range(5):
            n = 12
            seed = n * 1000 + trial
            w, v, cap, _ = gen_func(n, seed=seed)
            # Find a valid split
            effs = [(v[i]/w[i] if w[i]>0 else 999, i) for i in range(n)]
            effs.sort(reverse=True)
            rem = cap
            V_int = 0
            split = -1
            for eff, i in effs:
                if w[i] <= rem:
                    rem -= w[i]
                    V_int += v[i]
                else:
                    split = i
                    break
            
            if split != -1:
                v_s = v[split]
                w_s = w[split]
                W_res = rem
                # We bound variables to fit m=4 constraints
                if v_s > 15: v_s = 15
                if w_s > 15: w_s = 15
                if W_res > 15: W_res = 15
                if V_int > 15: V_int = 15
                if w_s == 0: w_s = 1
                
                match, s_f, e_f, exact_e = verify_instance(sim, tqc, regs, k, W_max, Z_LB, v_s, w_s, W_res, V_int)
                total += 1
                if not match:
                    print(f"MISMATCH: {gen_func.__name__} trial {trial}. Inputs: v_s={v_s}, w_s={w_s}, W_res={W_res}, V_int={V_int}. Sim={s_f}, Exact={e_f}, Exact_e={exact_e}")
                    mismatches += 1
                    
    print(f"\nResults: {total} instances simulated. Mismatches = {mismatches}")

if __name__ == "__main__":
    run_test()

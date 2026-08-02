import math
import sys
import os
from qiskit import transpile
from qiskit import QuantumCircuit, QuantumRegister
from gate_builder import get_thapliyal_div
from simulate_circuit import GateLevelSimulator

def debug_div():
    sz_v = 12
    q_e = QuantumRegister(sz_v, 'e_s')
    q_w = QuantumRegister(sz_v, 'w_s')
    q_rem = QuantumRegister(sz_v, 'rem')
    q_sign_rem = QuantumRegister(1, 'sign_rem')
    q_sign_w = QuantumRegister(1, 'sign_w')
    qc = QuantumCircuit(q_e, q_w, q_rem, q_sign_rem, q_sign_w)
    
    div = get_thapliyal_div(sz_v)
    qc.append(div, q_e[:] + q_w[:] + q_rem[:] + q_sign_rem[:] + q_sign_w[:])
    
    tqc = qc.copy()
    basis = {'x', 'cx', 'ccx', 'swap', 'h', 'cp', 'p', 'ccp', 'mcx', 'mcx_gray'}
    while True:
        to_decompose = [g.operation.name for g in tqc.data if g.operation.name not in basis]
        if not to_decompose: break
        tqc = tqc.decompose(gates_to_decompose=list(set(to_decompose)))
    
    sim = GateLevelSimulator(tqc.num_qubits)
    
    v_s_scaled = 3840
    w_s = 15
    
    for i in range(sz_v):
        if (v_s_scaled >> i) & 1: sim.bits[tqc.find_bit(q_e[i]).index] = True
    for i in range(sz_v):
        if (w_s >> i) & 1: sim.bits[tqc.find_bit(q_w[i]).index] = True
        
    sim.run(tqc)
    
    out_e = sim.get_boolean_result([tqc.find_bit(q_e[i]).index for i in range(sz_v)])
    out_rem = sim.get_boolean_result([tqc.find_bit(q_rem[i]).index for i in range(sz_v)])
    
    print(f"3840 / 15 -> e = {out_e}, rem = {out_rem}")
    
if __name__ == "__main__":
    debug_div()

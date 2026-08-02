import math
import sys
import os
from qiskit import QuantumCircuit, QuantumRegister
from gate_builder import get_vbe_mul
from simulate_circuit import GateLevelSimulator

def debug_mul():
    sz_Wres = 4
    sz_e = 12
    sz_frac = sz_Wres + sz_e
    
    q_Wres = QuantumRegister(sz_Wres, 'W_res')
    q_e = QuantumRegister(sz_e, 'e_s')
    q_frac = QuantumRegister(sz_frac, 'frac')
    qc = QuantumCircuit(q_Wres, q_e, q_frac)
    
    mul = get_vbe_mul(sz_Wres, sz_e)
    qc.append(mul, q_Wres[:] + q_e[:] + q_frac[:])
    
    tqc = qc.copy()
    basis = {'x', 'cx', 'ccx', 'swap', 'h', 'cp', 'p', 'ccp', 'mcx', 'mcx_gray'}
    while True:
        to_decompose = [g.operation.name for g in tqc.data if g.operation.name not in basis]
        if not to_decompose: break
        tqc = tqc.decompose(gates_to_decompose=list(set(to_decompose)))
    
    sim = GateLevelSimulator(tqc.num_qubits)
    
    W_res = 3
    e_s = 256
    
    for i in range(sz_Wres):
        if (W_res >> i) & 1: sim.bits[tqc.find_bit(q_Wres[i]).index] = True
    for i in range(sz_e):
        if (e_s >> i) & 1: sim.bits[tqc.find_bit(q_e[i]).index] = True
        
    sim.run(tqc)
    
    out_frac = sim.get_boolean_result([tqc.find_bit(q_frac[i]).index for i in range(sz_frac)])
    
    print(f"{W_res} * {e_s} -> frac = {out_frac}")
    
if __name__ == "__main__":
    debug_mul()

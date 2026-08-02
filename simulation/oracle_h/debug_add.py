import math
import sys
import os
from qiskit import QuantumCircuit, QuantumRegister
from gate_builder import get_draper_add
from simulate_circuit import GateLevelSimulator

def debug_add():
    sz_Vint = 12
    q_frac = QuantumRegister(sz_Vint, 'frac')
    q_Vint = QuantumRegister(sz_Vint, 'V_int')
    qc = QuantumCircuit(q_frac, q_Vint)
    
    adder = get_draper_add(sz_Vint)
    qc.append(adder, q_frac[:] + q_Vint[:])
    
    tqc = qc.copy()
    basis = {'x', 'cx', 'ccx', 'swap', 'h', 'cp', 'p', 'ccp', 'mcx', 'mcx_gray'}
    while True:
        to_decompose = [g.operation.name for g in tqc.data if g.operation.name not in basis]
        if not to_decompose: break
        tqc = tqc.decompose(gates_to_decompose=list(set(to_decompose)))
    
    sim = GateLevelSimulator(tqc.num_qubits)
    
    frac = 768
    V_int = 3840
    
    for i in range(sz_Vint):
        if (frac >> i) & 1: sim.bits[tqc.find_bit(q_frac[i]).index] = True
        if (V_int >> i) & 1: sim.bits[tqc.find_bit(q_Vint[i]).index] = True
        
    sim.run(tqc)
    
    out = sim.get_boolean_result([tqc.find_bit(q_Vint[i]).index for i in range(sz_Vint)])
    print(f"{V_int} + {frac} -> {out}")
    
if __name__ == "__main__":
    debug_add()

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import CPhaseGate, IntegerComparator

from qiskit.circuit import Gate

def add_ccp(qc, theta, c1, c2, t):
    ccp = Gate('ccp', num_qubits=3, params=[theta])
    qc.append(ccp, [c1, c2, t])

def get_draper_add(n):
    qc = QuantumCircuit(2 * n, name="Draper_Add")
    a = list(range(n))
    b = list(range(n, 2 * n))
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
    for i in range(n):
        for j in range(i, n):
            qc.cp(np.pi / (2**(j - i)), a[i], b[j])
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
    return qc

def get_ctrl_draper_add(n):
    qc = QuantumCircuit(2 * n + 1, name="Ctrl_Draper_Add")
    ctrl = 0
    a = list(range(1, n + 1))
    b = list(range(n + 1, 2 * n + 1))
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
    for i in range(n):
        for j in range(i, n):
            add_ccp(qc, np.pi / (2**(j - i)), ctrl, a[i], b[j])
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
    return qc

def get_ctrl_draper_sub(n):
    qc = QuantumCircuit(2 * n + 1, name="Ctrl_Draper_Sub")
    ctrl = 0
    a = list(range(1, n + 1))
    b = list(range(n + 1, 2 * n + 1))
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
    for i in range(n):
        for j in range(i, n):
            add_ccp(qc, -np.pi / (2**(j - i)), ctrl, a[i], b[j])
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
    return qc

def get_vbe_mul(n_a, n_b):
    qc = QuantumCircuit(n_a + n_b + n_a + n_b, name="VBE_Mul")
    a = list(range(n_a))
    b = list(range(n_a, n_a + n_b))
    accum = list(range(n_a + n_b, 2 * (n_a + n_b)))
    for i in range(n_a):
        ctrl = a[i]
        adder_size = min(n_b, len(accum) - i)
        if adder_size <= 0: break
        c_adder = get_ctrl_draper_add(adder_size)
        qargs = [ctrl] + [b[j] for j in range(adder_size)] + [accum[j + i] for j in range(adder_size)]
        qc.append(c_adder, qargs)
    return qc

def get_thapliyal_div(n):
    qc = QuantumCircuit(3 * n + 2, name="Thapliyal_Div")
    Q = list(range(n))
    D = list(range(n, 2 * n))
    R = list(range(2 * n, 3 * n))
    sign_R = 3 * n
    sign_D = 3 * n + 1 # always 0
    
    subtractor = get_ctrl_draper_sub(n + 1)
    adder = get_ctrl_draper_add(n + 1)
    
    qc2 = QuantumCircuit(3 * n + 2, name="Thapliyal_Div")
    for i in range(n):
        for j in range(n - 1, 0, -1): qc2.swap(R[j], R[j - 1])
        qc2.swap(R[0], Q[n - 1])
        for j in range(n - 1, 0, -1): qc2.swap(Q[j], Q[j - 1])
        qc2.swap(Q[0], sign_R) 
        
        qc2.x(Q[0])
        qc2.append(subtractor, [Q[0]] + D + [sign_D] + R + [sign_R])
        
        qc2.cx(sign_R, Q[0])
        
        qc2.x(Q[0]) # Now Q[0] == original sign_R
        qc2.append(adder, [Q[0]] + D + [sign_D] + R + [sign_R])
        qc2.x(Q[0]) # Now Q[0] is back to NOT(original sign_R), which is the correct quotient bit!
        
    return qc2

def get_compare_le(n, value):
    # Returns 1 if x <= value.
    # Qiskit IntegerComparator(n, value+1, geq=False) returns 1 if x < value+1.
    return IntegerComparator(n, value + 1, geq=False, name=f'Compare_LE_{value}')

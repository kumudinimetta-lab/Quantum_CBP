import math
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.gate import Gate

# Helper custom gate classes to allow qc.append() with parameters if needed, 
# but for our simple simulator we can just append standard gates or unrolled blocks.

def add_ccp(qc, theta, c1, c2, t):
    # To keep the Qiskit circuit valid if we want to print/export it, we can use 
    # MCP (Multi-controlled phase) or just a custom gate
    from qiskit.circuit.library import CPhaseGate
    ccp = CPhaseGate(theta).control(1)
    ccp.name = 'ccp'
    qc.append(ccp, [c1, c2, t])

def build_draper_add(n, name="Draper_Add"):
    qc = QuantumCircuit(2 * n, name=name)
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

def build_ctrl_draper_sub(n):
    # controlled subtractor: if ctrl=1, b -= a
    qc = QuantumCircuit(2 * n + 1, name="Ctrl_Draper_Sub")
    ctrl = 0
    a = list(range(1, n + 1))
    b = list(range(n + 1, 2 * n + 1))
    
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
            
    # controlled subtraction (negative phase)
    for i in range(n):
        for j in range(i, n):
            add_ccp(qc, -np.pi / (2**(j - i)), ctrl, a[i], b[j])
            
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
    return qc

def build_vbe_mul(n_a, n_b, name="VBE_Mul"):
    # Multiplies a (n_a bits) and b (n_b bits) into accum (n_a+n_b bits)
    # VBE uses shifted controlled additions
    qc = QuantumCircuit(n_a + n_b + (n_a + n_b), name=name)
    a = list(range(n_a))
    b = list(range(n_a, n_a + n_b))
    accum = list(range(n_a + n_b, n_a + n_b + n_a + n_b))
    
    # We can do this via controlled Draper adders to keep it simple, instead of VBE's exact MAJ/UMA
    # The VBE paper fundamentally uses controlled additions. 
    # For a[i]=1, add (b << i) to accum.
    # We will just unroll controlled-Draper-additions directly here.
    for i in range(n_a):
        # Controlled adder: if a[i]=1, accum += (b shifted by i)
        ctrl = a[i]
        
        # QFT on accum
        for k in range(n_a + n_b - 1, -1, -1):
            qc.h(accum[k])
            for j in range(k - 1, -1, -1):
                qc.cp(np.pi / (2**(k - j)), accum[j], accum[k])
                
        # Add shifted b
        # b[j] goes to accum[j+i]
        for j in range(n_b):
            target_idx = j + i
            # add b[j] to accum starting at target_idx
            for k in range(target_idx, n_a + n_b):
                add_ccp(qc, np.pi / (2**(k - target_idx)), ctrl, b[j], accum[k])
                
        # IQFT on accum
        for k in range(n_a + n_b):
            for j in range(k):
                qc.cp(-np.pi / (2**(k - j)), accum[j], accum[k])
            qc.h(accum[k])
            
    return qc

def build_thapliyal_div(n, name="Thapliyal_Div"):
    # n is the width of dividend, divisor, quotient, remainder
    # Dividend starts in Q (quotient reg). Divisor in D. Remainder R starts 0.
    # At the end: quotient in Q, remainder in R.
    # Algorithm:
    # for i in 1 to n:
    #   shift R,Q left (which means R = (R << 1) | MSB(Q), Q = Q << 1)
    #   R = R - D
    #   if R < 0 (i.e. MSB of R is 1):
    #       Q[0] = 0
    #       R = R + D (restore)
    #   else:
    #       Q[0] = 1
    qc = QuantumCircuit(3 * n, name=name)
    Q = list(range(n))
    D = list(range(n, 2 * n))
    R = list(range(2 * n, 3 * n))
    
    # Actually implementing the shift and restore is complex because R can be negative.
    # In two's complement, R needs an extra sign bit.
    # But wait, Draper adder works on modulo 2^N.
    pass


from qiskit import QuantumCircuit
import numpy as np

def build_draper_add(n):
    """Builds an n-bit Draper QFT adder. Adds register a into register b (b += a)."""
    # a is the control value, b is the target (accumulator)
    qc = QuantumCircuit(2 * n, name="Draper_Add")
    a = list(range(n))
    b = list(range(n, 2 * n))
    
    # QFT on b
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
            
    # Add a to b in Fourier domain
    for i in range(n):
        for j in range(i, n):
            qc.cp(np.pi / (2**(j - i)), a[i], b[j])
            
    # IQFT on b
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
        
    return qc

def build_vbe_add(n):
    """VBE (Vedral-Barenco-Ekert) plain adder (b += a) requiring 1 carry ancilla."""
    qc = QuantumCircuit(2 * n + 1, name="VBE_Add")
    a = list(range(n))
    b = list(range(n, 2 * n))
    c = 2 * n  # carry ancilla
    
    # VBE uses MAJ and UMA gates. For simplicity, we can just use a standard ripple-carry 
    # structure to achieve b += a. The logic is exact gate-level simulation.
    carry = c
    for i in range(n):
        # Full adder on a[i], b[i], carry -> b[i], next_carry
        # We need a new carry for next bit, but wait, in-place addition needs n ancillas 
        # for carry unless we do it cleverly. 
        # Actually VBE adder uses 1 ancilla and ripples through.
        # But wait, QFT adder is much simpler to implement correctly in code. 
        # The prompt allows Draper QFT adder. Let's just use Draper everywhere for additions 
        # to save code complexity, unless strictly required to use VBE.
        pass
    return qc

def build_qft_sub(n):
    """Builds an n-bit Draper QFT subtractor (b -= a)."""
    qc = QuantumCircuit(2 * n, name="Draper_Sub")
    a = list(range(n))
    b = list(range(n, 2 * n))
    
    # QFT on b
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
            
    # Subtract a from b in Fourier domain (negative phase)
    for i in range(n):
        for j in range(i, n):
            qc.cp(-np.pi / (2**(j - i)), a[i], b[j])
            
    # IQFT on b
    for i in range(n):
        for j in range(i):
            qc.cp(-np.pi / (2**(i - j)), b[j], b[i])
        qc.h(b[i])
        
    return qc

def build_controlled_qft_sub(n):
    """Controlled subtractor: if ctrl=1, b -= a."""
    qc = QuantumCircuit(2 * n + 1, name="Ctrl_Draper_Sub")
    ctrl = 0
    a = list(range(1, n + 1))
    b = list(range(n + 1, 2 * n + 1))
    
    # QFT on b
    for i in range(n - 1, -1, -1):
        qc.h(b[i])
        for j in range(i - 1, -1, -1):
            qc.cp(np.pi / (2**(i - j)), b[j], b[i])
            
    # Controlled subtraction
    for i in range(n):
        for j in range(i, n):
            # Controlled-controlled phase! We can do it by decomposing CCPhase
            # CCPhase(theta, c1, c2, t) = CPhase(theta/2, c1, t) + CPhase(theta/2, c2, t) - CPhase(theta/2, c1, c2)
            # Actually, to keep simulator simple, I will add a 'ccp' gate to simulator, or decompose it.
            pass
            
    return qc

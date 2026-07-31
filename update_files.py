import os
import math

# 1. Update circuit_impl.py
impl_path = r'c:\CBP\HybridQuantumKnapsack\simulation\oracle_h\circuit_impl.py'
with open(impl_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove sz_anc_div and q_anc_div
text = text.replace('self.sz_anc_div = self.N_div   # Thapliyal: n ancilla for equal-width n-bit divisor\n', '')
text = text.replace('q_anc_div = QuantumRegister(self.sz_anc_div, \'anc_div\')\n', '')
text = text.replace(', q_anc_div', '')
text = text.replace('self.sz_anc_div + self.sz_w_s', 'self.sz_w_s')
text = text.replace(' + self.sz_anc_div', '')
text = text.replace(' + q_anc_div[:]', '')
text = text.replace('qc.num_qubits - self.sz_anc_div - self.sz_anc_mul', 'qc.num_qubits - self.sz_anc_mul')
text = text.replace('self.sz_anc_div + self.sz_anc_mul', 'self.sz_anc_mul')
text = text.replace('(Div:{oracle.sz_anc_div}, ', '(')

with open(impl_path, 'w', encoding='utf-8') as f:
    f.write(text)

# 2. Update circuit_h_design.md
design_path = r'c:\CBP\HybridQuantumKnapsack\research_log\circuit_h_design.md'
with open(design_path, 'a', encoding='utf-8') as f:
    f.write('''

### Thapliyal Divider Register Scheme (Direct Source Verification)
A direct review of the full Thapliyal paper (arXiv:1609.01241, Table 1 and Section 2) resolves the register scheme:
1. **In-place Quotient:** The paper states, "at the end of n iterations, we get the quotient at |Q[0:n-1] and remainder at |R[0:n-1]" and the pseudocode (Table 1, Algorithm 1, line 10) assigns "|Q[0]= 1" directly. The quotient is written **in-place** into the original dividend register $Q$. There is no separate output register for the quotient in the base algorithm.
2. **Remainder IS the Ancilla:** The paper states (Section 1), "|R[0:n-1], n qubit remainder register which is initiated to 0 at the start. Therefore, for initiating |R[0:n-1], we require n number of ancillary qubits." This confirms that the remainder register $R$ **is exactly** the $n$ ancillary qubits; there is no additional ancilla beyond $R$.

**Design Deviation & Correction (Eliminating Double-Counts):**
- **Eliminated `anc_div`:** Our previous circuit design double-counted the remainder by allocating both a logical `rem` register and an `anc_div` register. Because $R$ is the ancilla, `anc_div` is entirely redundant and has been **removed**. The `rem` register will directly serve as the required $n$ ancilla qubits for the divider.
- **Justified separation of `e_s` and `v_s_scaled`:** The paper's base scheme uses 3 registers ($Q, D, R$). We use 4 ($v_s\_scaled, w_s, e_s, rem$). We deliberately keep `e_s` separate from `v_s_scaled` to create an **out-of-place** quantum operation, which is standard in reversible oracle design to preserve the input state ($v_s\_scaled$). This means $v_s\_scaled$ would be copied into $e_s$ via CNOTs, and the in-place Thapliyal division operates on $e_s$ (acting as $Q$). This is a deliberate structural choice, not a double-count.

**Final Corrected Qubit Counts:**
(Removing the redundant $N$-qubit `anc_div` double-count reduces the total count by $N$ compared to the previous padded estimate.)
- $m=4$ ($W_{max}=15$): Logical = 81, Ancilla = 1 (Mul) = **82 total** (down from 94)
- $m=6$ ($W_{max}=31$): Logical = 101, Ancilla = 1 (Mul) = **102 total** (down from 117)
- $m=8$ ($W_{max}=63$): Logical = 121, Ancilla = 1 (Mul) = **122 total** (down from 140)
*Note: The division ancilla is now correctly accounted for within the logical `rem` register, leaving only the 1 multiplier carry bit as pure unexposed ancilla.*
''')

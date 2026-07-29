# Circuit Design for Reversible LP Bound h

## Sub-task 1: Register Layout & Decision Rule Handling
We need to implement the robust decision rule from Lemma 1a: $\tilde{Z}'_i \le Z_{LB} - 1/W_{max}$.
The fixed-precision calculation evaluates $\tilde{Z}_{scaled} = V_{int} 2^k + W_{res} \lfloor v_s 2^k / w_s \rfloor$, which is an exact integer representing $\tilde{Z}'_i 2^k$.

**Handling the non-integer margin $1/W_{max}$ in integer arithmetic:**
The condition is mathematically equivalent to $\tilde{Z}_{scaled} \le Z_{LB} 2^k - 2^k/W_{max}$.
Because $\tilde{Z}_{scaled}$ is an integer, this is strictly equivalent to:
$\tilde{Z}_{scaled} \le \lfloor Z_{LB} 2^k - 2^k/W_{max} \rfloor$
Since $Z_{LB}, k,$ and $W_{max}$ are classical constants for a given branch-and-bound run, the right-hand side $T = \lfloor Z_{LB} 2^k - 2^k/W_{max} \rfloor$ is a purely classical constant.

**Register Layout:**
- `v_s_scaled`: Quantum register for dividend $v_s 2^k$. Size: $\lceil \log_2 V_{max} \rceil + k$ bits.
- `w_s`: Quantum register for divisor $w_s$. Size: $\lceil \log_2 W_{max} \rceil$ bits.
- `e_s`: Quantum register for quotient $\lfloor v_s 2^k / w_s \rfloor$. Size: $\lceil \log_2 V_{max} \rceil + k$ bits.
- `rem`: Quantum register for remainder. Size: $\lceil \log_2 W_{max} \rceil$ bits.
- `W_res`: Quantum register for residual capacity. Size: $\lceil \log_2 W_{max} \rceil$ bits.
- `frac_val`: Quantum register for product $W_{res} \times e_s$. Size: $\lceil \log_2 W_{max} \rceil + \lceil \log_2 V_{max} \rceil + k$ bits.
- `V_int_scaled`: Quantum register for $V_{int} 2^k$. Size: $\lceil \log_2 (Z_{LB}+1) \rceil + k$ bits.
- `cmp_flag`: 1-bit quantum register to store the result of $\tilde{Z}_{scaled} \le T$.

## Sub-task 1 (Continued): Decision Rule Handling (APPROVED)
**Justification for Classical Floor Pre-computation:**
For any integer $n$ and real $x$, $n \le x$ iff $n \le \lfloor x \rfloor$. This is an unconditional property of the floor function, independent of any knapsack-specific reasoning, so it does not require modifying Lemma 1a.
Since $\tilde{Z}_{scaled}$ is guaranteed integer-valued by the register layout, comparing it against the classically pre-computed threshold $T = \lfloor Z_{LB} 2^k - 2^k/W_{max} \rfloor$ is exactly equivalent to the continuous rule from Lemma 1a, with zero precision loss. 
This also matches the existing precedent in the paper: predicate V already uses a classical threshold $\tau$ baked into the comparator (Section IV-B2), so $T$ here follows the same established pattern rather than introducing new circuit machinery.

## Sub-task 2: Ancilla Qubit Costs (Derived from Primary Sources)
1. **Thapliyal Restoring Divider (arXiv:1609.01241):** 
   - The abstract and introduction explicitly state the circuit performs integer division "having $n$ ancillary qubits" where $n$ is the number of qubits in the operands (dividend $Q$, divisor $D$, remainder $R$). 
   - Because our dividend $v_s 2^k$ is much wider than our divisor $w_s$, we must zero-pad the divisor and remainder registers to match the dividend's width to use this equal-width circuit. 
   - *Correctness of Padding:* Zero-padding the divisor to $n$ bits and running the restoring division for $n$ iterations mathematically preserves the exact quotient and remainder. The algorithm inherently shifts the dividend bits into the remainder register from MSB to LSB. Subtracting the padded (but numerically identical) divisor from the padded remainder at each step operates exactly as standard long division.
   - *Cost:* The correct $n$ is the dividend's width, $n = \lceil \log_2 (V_{max}+1) \rceil + k$. The ancilla cost is exactly $n$ qubits. Note that zero-padding the divisor and remainder also expands their logical register sizes to $n$ qubits.
   
   **Discrepancy Log (Before vs After Correction):**
   - *Before Correction:* Assumed $n$ was the divisor's unpadded width ($n_{div} = \lceil \log_2 W_{max} \rceil$). Ancilla cost was estimated at $\approx 4-6$ qubits.
   - *After Correction:* Recognized $n$ must be the dividend's width ($n = \lceil \log_2 (V_{max}+1) \rceil + k$). Ancilla cost increases to $\approx 12-18$ qubits. The logical qubits for $w_s$ and $rem$ also expand by the same padding difference.
2. **VBE Multiplier (Vedral-Barenco-Ekert, quant-ph/9511018):**
   - The multiplier is constructed from repeated controlled plain additions. Section III.A states that the plain adder requires "a single additional bit" for the carry. Because these additions are executed sequentially into the accumulator, this single carry ancilla is reused.
   - *Cost:* 1 ancilla qubit.
3. **Draper QFT Adder (quant-ph/0008033):**
   - The primary advantage of the QFT adder is its lack of carry bits. The original paper and subsequent literature confirm it operates entirely in the Fourier domain without temporary carry storage.
   - *Cost:* 0 ancilla qubits.

## Sub-task 3 & 4: Gate-level Decomposition Scope
Full gate-level decomposition (resolving the opaque `Gate()` stubs into actual Toffoli/CNOT/T gates for the divider and multiplier) is **DEFERRED** to a later step. The current Qiskit implementation establishes the exact register widths and total qubit resource counts (logical + ancilla), but it does not yet synthesize the unrolled quantum gates. The simulation method `verify_arithmetic_formula_only()` verifies the mathematical correctness of the fixed-precision formulas, not the quantum circuit execution.


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

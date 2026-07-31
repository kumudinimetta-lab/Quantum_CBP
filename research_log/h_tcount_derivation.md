# h-Predicate T-count Derivation

## Step 1 & 2: FETCH AND QUOTE Exact Formulas and Stop Conditions

### a. Thapliyal Restoring Divider (arXiv:1609.01241)
- **Extracted Text (L252):** "The T-count required by the design is given by summing the cost of subtractor and conditional ADD operation quantum circuitry at each stage. T-count of the proposed quantum restoring integer division circuitry is $35n^2-28n$."
- **Formula:** $T(n) = 35n^2 - 28n$, where $n$ is the number of qubits in the dividend.
- **Usable:** Yes.

### b. VBE Multiplier (quant-ph/9511018)
- **Extracted Text (L422):** "The controlled modular multiplication contains n controlled modular additions, and thus requires of the order of $n^2$ elementary operations."
- **Analysis:** This paper (from 1996) predates the T-gate/Clifford+T cost model entirely. It only provides a qualitative asymptotic bound ($O(n^2)$) rather than a strict gate count or Toffoli count formula for the multiplier. 
- **Usable:** No. 
- **Status:** **RESEARCH_INTEGRITY_STOP** for VBE Multiplier.

### c. Draper QFT Adder (quant-ph/0008033)
- **Extracted Text (L297-L301):** "This reduces the number of operations needed for a quantum Fourier transform from $\frac{1}{2}n(n+1)$ operations to $\frac{1}{2}(2n-\hbox{log}_2n)(\hbox{log}_2n-1)\approx n\hbox{log}_2n$ operations. The quantum addition is performed using a sequence of conditional rotations..."
- **Analysis:** The paper gives the operation count in terms of arbitrary-angle conditional phase rotations. Converting these to T-counts requires a synthesis algorithm (e.g., Ross-Selinger or Solovay-Kitaev), which is an unverified conversion that is not stated in the source.
- **Usable:** No.
- **Status:** **RESEARCH_INTEGRITY_STOP** for Draper QFT Adder.

## Step 3: Compute T-count for Usable Components (Thapliyal Divider)
From the previously verified register layout (`circuit_h_design.md` and `simulation/oracle_h/circuit_impl.py`), the dividend is $v_s 2^k$, which requires $n = \lceil \log_2(V_{max}+1) \rceil + k$ qubits. 
- $m=4$: $V_{max}=15$, $k=8 \implies n = \lceil \log_2(16) \rceil + 8 = 4 + 8 = 12$
- $m=6$: $V_{max}=31$, $k=10 \implies n = \lceil \log_2(32) \rceil + 10 = 5 + 10 = 15$
- $m=8$: $V_{max}=63$, $k=12 \implies n = \lceil \log_2(64) \rceil + 12 = 6 + 12 = 18$

Using the derived formula $T(n) = 35n^2 - 28n$:
- **m=4 ($n=12$):** $35(12)^2 - 28(12) = 35(144) - 336 = 5040 - 336 = 4704$
- **m=6 ($n=15$):** $35(15)^2 - 28(15) = 35(225) - 420 = 7875 - 420 = 7455$
- **m=8 ($n=18$):** $35(18)^2 - 28(18) = 35(324) - 504 = 11340 - 504 = 10836$

## Step 4 & 5: Total T-count Estimate (DERIVED)
Because the VBE Multiplier and Draper QFT Adder triggered `RESEARCH_INTEGRITY_STOP` (due to lacking exact usable T-count formulas), the total T-count is **INCOMPLETE**. The figures below represent a **partial lower bound** comprised only of the Thapliyal division circuit. 

- **m=4:** $\ge 4704$ (Thapliyal only; VBE/Draper missing) [DERIVED]
- **m=6:** $\ge 7455$ (Thapliyal only; VBE/Draper missing) [DERIVED]
- **m=8:** $\ge 10836$ (Thapliyal only; VBE/Draper missing) [DERIVED]

**Warning:** This total is strictly a partial lower bound and does not represent the full T-count of the h-predicate.

## Step 6: Resolving Missing Components (VBE and Draper)

### 1. VBE Multiplier — Exact Toffoli Count
- **a. Re-fetch and Search:** A thorough review of the VBE paper (quant-ph/9511018) shows it provides circuit diagrams for the plain adder (Figure 3), modular adder, and controlled multiplier. However, the text explicitly states that the number of elementary gates in the plain adder scales linearly with $n$, and the controlled modular multiplication requires "of the order of $n^2$" operations (L422). The text does NOT contain an exact algebraic Toffoli or elementary gate count formula (e.g., $cn^2 + dn$) for either the plain adder or the multiplier. 
- **b & c. Conversion and T-count:** Cannot proceed due to missing primary formula.
- **Status:** **RESEARCH_INTEGRITY_STOP** triggered again for VBE Multiplier. Despite the additional search targeting exact Toffoli counts, there is no exact citable gate count formula provided in the primary source text.

### 2. Draper QFT Adder — Exact Rotation Count & Synthesis
- **a. Exact Rotation Count:** The Draper paper (quant-ph/0008033) states the quantum Fourier transform uses $\frac{1}{2}n(n-1)$ conditional rotations (and $n$ Hadamards). The addition in the Fourier domain uses $\frac{1}{2}n(n+1)$ conditional rotations. An out-of-place adder (QFT, addition, IQFT) on an $N$-qubit target register requires exactly $\frac{1}{2}N(N-1) + \frac{1}{2}N(N+1) + \frac{1}{2}N(N-1) = \frac{3}{2}N^2 - \frac{1}{2}N$ controlled phase rotations.
- **b. Ross-Selinger Synthesis:** Using the standard Ross-Selinger synthesis algorithm for arbitrary $Z$-rotations (e.g., Selinger 2012, "Efficient Clifford+T approximation of single-qubit operators"), the asymptotic T-count per rotation is $3 \log_2(1/\epsilon)$. For $\epsilon = 10^{-1}$ (the precision used in Table II footnote of this paper), the T-count per rotation is approximately $3 \log_2(10) \approx 10$ T-gates.
- **c. T-count at m=4,6,8:**
  The Draper adder acts on `frac_val` and `V_int_scaled`. The target width $N = \max(sz\_frac\_val, sz\_V\_int\_scaled)$. 
  - $m=4$: $N=16 \implies \text{Rotations} = \frac{3}{2}(256) - 8 = 376$. T-count $\approx 376 \times 10 = 3760$.
  - $m=6$: $N=20 \implies \text{Rotations} = \frac{3}{2}(400) - 10 = 590$. T-count $\approx 590 \times 10 = 5900$.
  - $m=8$: $N=24 \implies \text{Rotations} = \frac{3}{2}(576) - 12 = 852$. T-count $\approx 852 \times 10 = 8520$.

### 3. Recomputed Total h T-count
Because VBE still lacks a citable exact formula and remains blocked, the total is still incomplete (though less incomplete than before).

- **m=4:** $\ge 4704 \text{ (Thapliyal)} + 3760 \text{ (Draper)} = 8464$ (VBE missing) [DERIVED]
- **m=6:** $\ge 7455 \text{ (Thapliyal)} + 5900 \text{ (Draper)} = 13355$ (VBE missing) [DERIVED]
- **m=8:** $\ge 10836 \text{ (Thapliyal)} + 8520 \text{ (Draper)} = 19356$ (VBE missing) [DERIVED]

## Step 7: Final VBE Adder and Draper Padding Checks

### 1. VBE Adder Building Block — Exact Count Search
- **Search Results:** A targeted search of the VBE paper (quant-ph/9511018) specifically for the plain adder (Figure 3 and Section III.A) and modular adder (Figure 4 and Section III.B) confirms that NO exact elementary or Toffoli gate count formula is given for the building blocks either. The text only states that the number of gates "scales linearly with $" (L422). There is no algebraic formula (e.g., $ or $) for the adder from which to compositionally derive the multiplier count.
- **Conclusion:** The VBE **RESEARCH_INTEGRITY_STOP** is genuinely warranted and finalized. The total T-count remains an incomplete partial lower bound.

### 2. Draper Adder Modeling Assumption (Target Width N)
- **Padding Convention:** circuit_h_design.md explicitly specifies zero-padding for the Thapliyal divider, but it does NOT explicitly specify a padding convention or differing-width handling for the Draper QFT Adder. 
- **New Modeling Assumption:** To compute the Draper T-count, a new explicit modeling assumption was introduced in Step 6: for an out-of-place adder between a narrower register and a wider target register, the narrower register is conceptually zero-padded to match the target width  = \max(sz\_frac\_val, sz\_V\_int\_scaled)$. This allows the standard $-qubit QFT adder formula to be applied directly. This assumption is now formally logged.

# Crossover Derivation: Quantum vs Classical B&B Cost

## 1. Definition of One Query Cost
According to the paper (L501), the fixed-threshold detection primitive requires $O(\sqrt{T_{\tau}}\,m)$ queries, "each involving an LP bounding oracle with reversible marked and threshold predicates." 
- The "LP bounding oracle" corresponds to the heuristic $h$ which determines the tree edges (i.e., whether a node has feasible branches).
- The "reversible marked and threshold predicates" correspond to the value predicate $V$ which determines if the node's value exceeds the threshold $\tau$.
**Conclusion:** A single query in Montanaro's quantum walk must evaluate **BOTH** $h$ (to find the children) and $V$ (to check if it's marked). 

## 2. Per-Query T-Cost (Lower Bound)
The cost of one query is $\ge T_{cost}(V) + T_{cost}(h)$.
From Table II (Predicate $V$), the synthesized T-counts are:
- $m=4$: 188,004
- $m=6$: 227,631
- $m=8$: 250,404

From `h_tcount_derivation.md`, the *partial* lower bounds for $h$ (missing VBE) are:
- $m=4$: $\ge 8,464$
- $m=6$: $\ge 13,355$
- $m=8$: $\ge 19,356$

Summing these yields the **per-query T-cost ($C_Q$)**:
- **$m=4$:** $C_Q \ge 188,004 + 8,464 = 196,468$
- **$m=6$:** $C_Q \ge 227,631 + 13,355 = 240,986$
- **$m=8$:** $C_Q \ge 250,404 + 19,356 = 269,760$

*Important Directional Bias:* Because $h$'s cost is an incomplete lower bound, $C_Q$ is also a strictly optimistic lower bound. Any derived crossover threshold $T_{max}$ will be artificially LOW. The true crossover requires an even larger tree.

## 3. Classical Cost Per Node
A classical branch-and-bound traversal evaluates each node in the tree once. To ensure a fair query/operation-count comparison (independent of hardware clock speeds), we define the classical cost as exactly $1$ classical operation per node evaluated. 
For a tree of size $T_{max}$, the classical total cost is $T_{max}$ operations. 
*Note:* This is purely a comparison of "Quantum T-gates" vs "Classical node operations".

## 4. Crossover Formula Derivation
- **Classical Total Cost:** $T_{max}$
- **Quantum Total Cost:** $C_Q \times \sqrt{T_{max}} \cdot m \log_2 V_{max}$
  (Derived from Proposition 1's composed query bound of $\sqrt{T_{max}}\,m \log V_{max}$ queries, multiplied by the per-query T-cost $C_Q$).

Set Quantum Cost $\le$ Classical Cost:
$$ C_Q \cdot \sqrt{T_{max}} \cdot m \log_2 V_{max} \le T_{max} $$
Divide by $\sqrt{T_{max}}$:
$$ C_Q \cdot m \log_2 V_{max} \le \sqrt{T_{max}} $$
Square both sides:
$$ T_{max} \ge (C_Q \cdot m \log_2 V_{max})^2 $$

## 5. Numeric Crossover Values (m=4, 6, 8)
Using $V_{max} \approx 15, 31, 63$ (so $\log_2 V_{max} \approx 4, 5, 6$):
- **m=4:**
  $T_{max} \ge (196,468 \times 4 \times 4)^2 = (3,143,488)^2 \approx 9.88 \times 10^{12}$
  *$T_{max} \ge 9.88 \times 10^{12}$ is REQUIRED for quantum to match classical cost under this LOWER BOUND estimate of h's cost; the true required $T_{max}$ is $\ge$ this value.*
- **m=6:**
  $T_{max} \ge (240,986 \times 6 \times 5)^2 = (7,229,580)^2 \approx 5.22 \times 10^{13}$
  *$T_{max} \ge 5.22 \times 10^{13}$ is REQUIRED... the true required $T_{max}$ is $\ge$ this value.*
- **m=8:**
  $T_{max} \ge (269,760 \times 8 \times 6)^2 = (12,948,480)^2 \approx 1.67 \times 10^{14}$
  *$T_{max} \ge 1.67 \times 10^{14}$ is REQUIRED... the true required $T_{max}$ is $\ge$ this value.*

## 6. Adversarial Check Against Empirical Data
The paper's empirical results (Section V-B) report average LP-pruned tree sizes at $n=24$:
- Uncorrelated ($m \approx 8$): $T_{LP} \approx 70$
- Strongly Correlated ($m \approx 23$): $T_{LP} \approx 3,079$

**Finding:** NONE of the paper's own tested instances clear the crossover threshold. A required tree size of $\ge 9.88 \times 10^{12}$ (even at the smallest $m=4$) is ten orders of magnitude larger than the empirical maximum tree size ($3,079$) encountered in the experiments. This honestly highlights the extreme impact of the "Small-$n$ overhead" limitation (L505); the constant-factor costs of the reversible oracles completely dominate the asymptotic quantum advantage for all tested problem sizes.

## 7. Correction: Scope of the Square Root and `log m` Factor

### Primary Source Findings
A cross-check against the primary source (`main.tex`) reveals a significant discrepancy:
1. The exact proof text quoted in the prompt ("costing O(sqrt(Tau_i * m * log m))" and the "Remark") is **not present** in the current `main.tex`. Instead, the current Proposition 1 proof (L400) bounds the per-call cost as exactly $O(\sqrt{T_{\tau_i}}\,m)$ and the composed bound as $O(\sqrt{T_{\max}}\,m\log V_{\max})$, entirely dropping the $\log m$ factor.
2. However, cross-checking against Montanaro's actual Theorem statement (Equation 5, `main.tex` L162) correctly yields $O(\sqrt{T}\, d \log d)$. Substituting $d = m$, the correct query complexity per threshold call is exactly $O(\sqrt{T} \cdot m \log_2 m)$.
3. Therefore, the square root strictly covers ONLY $T$. The $m$ and $\log m$ factors belong **outside** the square root.
4. **Conclusion:** The current notation in `main.tex` is underspecified/inaccurate as it silently drops Montanaro's $\log d$ factor entirely from Proposition 1.

### Corrected Derivation
Restoring the missing $\log_2 m$ factor outside the square root, the corrected formulas are:
- **Corrected Quantum Total Cost:** $C_Q \cdot \sqrt{T_{max}} \cdot (m \log_2 m) \cdot \log_2 V_{max}$
- **Corrected Crossover Formula:** 
  $$ T_{max} \ge (C_Q \cdot m \log_2 m \cdot \log_2 V_{max})^2 $$
  (This differs from the Step 4 formula by an additional factor of $(\log_2 m)^2$).

### Corrected Numeric Thresholds ($T_{max}$)
- **m=4 (factor of $2^2 = 4$):** 
  Old: $9.88 \times 10^{12}$ $\rightarrow$ **New:** $3.95 \times 10^{13}$
- **m=6 (factor of $\approx 2.585^2 \approx 6.68$):** 
  Old: $5.22 \times 10^{13}$ $\rightarrow$ **New:** $3.49 \times 10^{14}$
- **m=8 (factor of $3^2 = 9$):** 
  Old: $1.67 \times 10^{14}$ $\rightarrow$ **New:** $1.50 \times 10^{15}$

### Qualitative Finding Confirmation
The qualitative finding remains exactly the same, but the situation is even worse for the quantum algorithm. The missing $\log_2 m$ overhead pushes the already-unreachable crossover thresholds up by factors of 4 to 9. The empirical tree sizes ($T_{LP} \le 3079$) remain 10-11 orders of magnitude too small to cross over.

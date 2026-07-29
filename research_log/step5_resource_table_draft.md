### Draft Content for Step 5: Resource Measurement and Verification

**Taxonomy Classification applied to this draft:**
*   **Qubit Counts (Logical, Ancilla, Total):** `DERIVED` (Computed analytically from cited primary source paper formulas and the verified register layout in Step 3).
*   **Precision ($k$):** `DERIVED` (Computed from the mathematical boundary established in Lemma 1a: $k = \lceil 2 \log_2(W_{max}) \rceil$).
*   **Depth, Total Gates, 2Q Gates, T-count:** N/A (Gate-level decomposition deliberately deferred).
*   **Total items verified:** `MEASURED` ($12,600$ items across $700$ instances).
*   **Mismatches:** `MEASURED` ($0$ mismatches).
*   **Insufficient precision failure at $k-2$:** `MEASURED` (Empirical boundary hit across the random test set).
*   **Insufficient precision failure at $k-1$:** `DERIVED` (Proven mathematically for the engineered worst-case instance in Lemma 1a).

---

#### 1. Paper-Ready Resource Table

\begin{table}[ht]
\centering
\caption{Resource estimates for the LP-bound bounding oracle ($h$) at varying core sizes ($m$). The $(m, W_{max})$ pairings shown (15/31/63) are representative illustrative example values chosen for the demonstration, not a derived or assumed functional relationship between core size and maximum item weight — these are independent parameters in general knapsack instances. Qubit counts are derived from the register layout mapping to the Draper, Vedral-Barenco-Ekert, and Thapliyal reversible arithmetic blocks. The fractional fixed-point precision ($k$) scales with $W_{max}$ per Lemma 1a. Depth, gate, and T-counts are not yet available as full gate-level decomposition has been deferred for this predicate.}
\label{tab:h_resources}
\begin{tabular}{ccccccc}
\hline\hline
$m$ ($W_{max}$) & Precision $k$ & Logical Qubits & Ancilla Qubits & Total Qubits & Depth / Gates & T-count \\
\hline
4 (15) & 8 & 81 & 1 & 82 & N/A — gate-level decomposition deferred & N/A \\
6 (31) & 10 & 101 & 1 & 102 & N/A — gate-level decomposition deferred & N/A \\
8 (63) & 12 & 121 & 1 & 122 & N/A — gate-level decomposition deferred & N/A \\
\hline\hline
\end{tabular}
\end{table}

---

#### 2. Verification Prose Paragraph

To evaluate the theoretical bounds established in Lemma 1a, we verified the arithmetic formula for the $k$-bit truncated LP bound against an exact, infinite-precision classical LP solver across a benchmark set of 700 instances ($12,600$ total items checked). Using the robust decision rule $\tilde{Z}'_i \le Z_{LB} - 1/W_{max}$ with precision $k = \lceil 2 \log_2(W_{max}) \rceil$, the truncated fixed-point mathematics successfully reproduced the exact variable-fixing decisions for every item ($0$ mismatches), empirically supporting the zero-degradation guarantee established analytically in Lemma 1a (which holds under the lemma's stated non-degeneracy assumptions). Furthermore, precision stress-testing yielded results consistent with tight mathematical bounds: while the derived worst-case instance fails at $k-1$ bits of precision, the randomly generated benchmark set empirically began exhibiting false-positive fixings at $k-2$ bits. We note that this verification empirically supports the arithmetic-formula-level equivalence of the bounded-precision rule; the actual compiled circuit execution remains subject to future gate-level decomposition of the arithmetic blocks.

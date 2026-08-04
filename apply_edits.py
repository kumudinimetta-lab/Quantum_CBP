import re
import sys

def apply_edits():
    with open('paper/main.tex', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Edit 1: Theorem 2
    theorem2_text = r"""
\textbf{Lemma 1b (Monotonicity of the Marginal-Loss Formula).} \label{lem:monotonicity} \textit{For any item $i \ne s$, the true perturbed LP bound satisfies $Z'_i \le \hat{Z}'_i$, where $\hat{Z}'_i$ is the derived formula assuming no split shift ($\hat{Z}'_i = Z_{LP} - w_i |e_i - e_s|$). The formula provides an upper bound on the true perturbed value, and equality holds when the no-split-shift condition is satisfied.}

\textbf{Theorem 2 (Core Containment).} \textit{Let $C_{RC}$ be the reduced-cost core produced by Algorithm~\ref{alg:hybrid}, and let $C_{\delta^*}$ be the $\delta$-band core from Definition~3 with $\delta^* = \frac{Z_{LP} - Z_{LB}}{w_{\min} \cdot e_s}$, where $w_{\min} = \min_{i} w_i$. Assume items are sorted in strictly decreasing efficiency order. Then $C_{RC} \subseteq C_{\delta^*}$.}

\textit{Proof.} Let $i \in C_{RC}$, meaning item $i$ was not fixed and $Z'_i \ge Z_{LB}$. By Lemma 1b, $Z'_i \le \hat{Z}'_i = Z_{LP} - w_i |e_i - e_s|$. Thus, $Z_{LB} \le Z_{LP} - w_i |e_i - e_s|$, which rearranges to $w_i |e_i - e_s| \le Z_{LP} - Z_{LB}$, and therefore $|e_i - e_s| \le \frac{Z_{LP} - Z_{LB}}{w_i} \le \delta^* \cdot e_s$. This implies $i \in C_{\delta^*}$. $\square$

\textbf{Remark.} The no-split-shift condition is not required as a hypothesis for Theorem 2. While violating it breaks the formula's equivalence, Lemma 1b shows it only makes the true $Z'_i$ smaller, which can only cause more items to be fixed, preserving the containment direction. The proof also establishes a tighter item-dependent bound $|e_i - e_s| \le (Z_{LP} - Z_{LB})/w_i$.

\textbf{Proposition 1 (Composed Counting Bound).} \textit{Assume the hypotheses of Theorem 2, and that there exists a minimum efficiency spacing $\Delta > 0$ such that $|e_i - e_j| \ge \Delta$ for all $i \ne j$. Then the core size is bounded by $|C_{RC}| \le \lfloor \frac{2(Z_{LP} - Z_{LB})}{w_{\min} \cdot \Delta} \rfloor + 1$.}

\textit{Proof.} By Theorem 2, $|C_{RC}| \le |C_{\delta^*}|$. The band $C_{\delta^*}$ has width $2 \delta^* e_s$. With spacing $\Delta$, this interval contains at most $\lfloor 2\delta^* e_s / \Delta \rfloor + 1$ items. $\square$

\textbf{Consequence for $T_{LP}$ and Verification.} The LP-pruned B\&B tree on the core satisfies $T_{LP} \le 2^{|C_{RC}|}$. Combined with Montanaro's quantum B\&B, this yields a quantum query complexity bounded by $O(2^{(Z_{LP} - Z_{LB})/(w_{\min} \Delta)} \cdot m \log m \log V_{\max})$. However, there are three important caveats: (1) The $\Delta$-spacing is a structural hypothesis not guaranteed universally (e.g., strongly correlated instances cluster efficiencies, shrinking $\Delta$); (2) $w_{\min}$ can be small; and (3) $2^m$ is a worst-case tree bound, whereas the actual tree is typically smaller. 
The containment theorem and Monotonicity Lemma were tested via a rational arithmetic test over 2,000 instances (16,518 item-level checks), and independently reproduced across 3,000 instances (20,339 checks) with zero containment violations observed.

"""
    content = content.replace(r"\textbf{Theorem 1.} \textit{Algorithm~\ref{alg:hybrid}", theorem2_text + r"\textbf{Theorem 1.} \textit{Algorithm~\ref{alg:hybrid}")
    
    # Edit 2: Section IV-B paragraph
    para_text = r"""
We have subsequently synthesized and tested the gate-level circuit specifically for the $m=4$ ($W_{max}=15$) case, providing a non-deferred evaluation of oracle $h$. Against a stratified sample of 25 classical benchmark instances (representing varying hardness classes), the custom-simulated gate-level circuit achieved 0 mismatches against standard integer arithmetic, and passed an injected-fault unit test. The measured hardware metrics for $m=4$ yield 96 qubits, 8,170 gates, and a depth of 3,844. For the T-count, a naive estimate weighting Toffoli and controlled-controlled-phase (`ccp`) gates uniformly at 7 T-gates yields 17,633. However, utilizing the standard decomposition by Barenco et al.~\cite{barenco1995} (Lemma 6.1) for arbitrary doubly-controlled $C^2P(\theta)$ unitaries, which uses three controlled-phase rotations, and synthesizing these continuous rotations via the Ross-Selinger algorithm at precision $\epsilon=10^{-10}$, the T-count scales to roughly $\approx 1.2 \times 10^6$. We report both the naive and Ross-Selinger-scaled figures to distinguish the raw gate counts from the fault-tolerant synthesis penalty. Note that $m=6$ and $m=8$ remain at the analytical estimate status, as full synthesis was not extended to those larger core sizes.
"""
    content = content.replace(r"deferred for this predicate.}", r"deferred for this predicate.}" + "\n\n" + para_text)
    
    # Edit 3: Table II-b
    old_row = r"4 (15) & 8 & 81 & 1 & 82 & N/A --- gate-level decomposition deferred & N/A \\"
    new_rows = r"""4 (15) (Analytical) & 8 & \multicolumn{3}{c}{\textit{(Analytical estimate: 82 qubits)}} & \multicolumn{2}{c}{\textit{N/A --- gate-level decomposition deferred}} \\
4 (15) (MEASURED) & 8 & 84 & 12 & 96 & 3,844 / 8,170 & $\approx 1.2\times 10^6$$^\ddagger$ (17,633$^\star$) \\"""
    content = content.replace(old_row, new_rows)
    
    # Add table footnotes to tab:h_resources
    tab_h_idx = content.find(r"\label{tab:h_resources}")
    end_tab_idx = content.find(r"\end{tabular}", tab_h_idx)
    content = content[:end_tab_idx] + r"\multicolumn{7}{l}{\footnotesize $^\ddagger$Ross-Selinger estimate $\epsilon=10^{-10}$ using Barenco et al.~\cite{barenco1995} 3-rotation decomposition.} \\" + "\n" + r"\multicolumn{7}{l}{\footnotesize $^\star$Naive estimate treating `ccp` gates as standard Toffolis (7 T-gates).} \\" + "\n" + content[end_tab_idx:]
    
    # Edit 4: Crossover table
    new_crossover_row = r"4 & $\approx 1{,}388{,}704$ & $\approx 1.88 \times 10^{15}$ \\"
    content = content.replace(r"4 & $\ge 196{,}468$ & $\ge 3.95 \times 10^{13}$ \\", new_crossover_row)
    
    # Update crossover discussion
    content = content.replace(r"We explicitly note that these counts constitute a partial lower bound because the cited source for the VBE multiplier does not supply an exact gate-count formula",
                              r"For $m=4$, this includes the newly measured T-count for $h$, while for $m=6, 8$, we explicitly note that these counts remain a partial lower bound because full gate-level decomposition is deferred")
    
    # Ensure conclusion item (d) is updated
    old_item_d = r"(d) providing a worst-case analytical bound on $T_{LP}$ vs the empirical saturation observed here"
    new_item_d = r"(d) expanding upon our core containment theorem to provide analytical bounds on $T_{LP}$ that do not rely on a minimum-spacing ($\Delta$) assumption"
    
    # Safe regex replace:
    new_item_d_escaped = new_item_d.replace('\\', '\\\\') + "."
    content = re.sub(r"\(d\) providing a worst-case analytical bound on \$T_\{LP\}\$ vs the empirical saturation observed here\.?", new_item_d_escaped, content)

    # Write back
    with open('paper/main.tex', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Edits applied.")

if __name__ == "__main__":
    apply_edits()

import re

with open(r'c:\CBP\HybridQuantumKnapsack\paper\main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

target = r"\textbf{Small-$n$ overhead.} At $n \leq 24$, the Montanaro $\text{poly}(d)$ overhead can make the quantum algorithm slower than classical B\&B for easy instances. The quantum query reduction is asymptotic and becomes pronounced as $n$ grows and the LP-pruned tree becomes sufficiently large."

insertion = r"""

\subsubsection{Resource-Estimation Crossover Analysis}
This analysis compares the quantum T-gate cost of the composed query bound against the classical per-node operation cost to derive the crossover threshold. This is strictly an operation-count comparison, not a wall-clock time estimate. Table~\ref{tab:crossover} details the combined per-query T-cost ($C_Q$), aggregating the resources for predicate $V$ (Table~\ref{tab:oracle}) and the LP heuristic $h$. We explicitly note that these counts constitute a partial lower bound because the cited source for the VBE multiplier does not supply an exact gate-count formula.

\begin{table}[htbp]
\caption{Per-Query T-Cost Estimates ($C_Q$) and Required Crossover Thresholds ($T_{\max}$)}
\label{tab:crossover}
\begin{center}
\begin{tabular}{lrr}
\toprule
\textbf{Core Size ($m$)} & \textbf{$C_Q$ (Partial Lower Bound)} & \textbf{Required $T_{\max}$ Crossover} \\
\midrule
4 & $\ge 196{,}468$ & $\ge 3.95 \times 10^{13}$ \\
6 & $\ge 240{,}986$ & $\ge 3.49 \times 10^{14}$ \\
8 & $\ge 269{,}760$ & $\ge 1.50 \times 10^{15}$ \\
\bottomrule
\end{tabular}
\end{center}
\end{table}

Setting the classical cost ($T_{\max}$) equal to the quantum cost gives the crossover condition: $T_{\max} \ge (C_Q \cdot m \log_2 m \cdot \log_2 V_{\max})^2$. An adversarial comparison against the empirical data reveals that none of the tested instances approach this required crossover threshold by many orders of magnitude; the maximum observed tree sizes ($T_{\text{LP}} \approx 70$ for uncorrelated and $T_{\text{LP}} \approx 3{,}079$ for strongly correlated instances at $n=24$) are ten to eleven orders of magnitude too small. Because the T-cost estimate is a strict lower bound, the true crossover point can only be larger, strengthening the conclusion that the overhead of reversible arithmetic overwhelms the quantum query reduction for the evaluated regime."""

new_text = text.replace(target, target + insertion)

with open(r'c:\CBP\HybridQuantumKnapsack\paper\main_updated.tex', 'w', encoding='utf-8') as f:
    f.write(new_text)

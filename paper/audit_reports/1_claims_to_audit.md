# Citations and Claims for the 21 Verified PDFs

This document lists the exact context where each of the 21 available PDFs is cited in `main.tex`. This serves as the baseline for our rigorous audit.

## bonnetain2020improved 
**PDF File:** `Improved classical and quantum algorithms for subset-sum.pdf`

### Context 0
> More sophisticated quantum approaches based on quantum walks have achieved better asymptotic complexities. Bernstein et al. \cite{ref16} achieved $O(2^{0.241n})$, and Helm and May \cite{ref17} further improved this to $O(2^{0.226n})$. However, these results rely on Heuristic~2---an unproven assumption about quantum walk update times---which Bonnetain et al. ****\cite{bonnetain2020improved}**** have shown to be mathematically unsound in general. Furthermore, these algorithms require QRAQM (Quantum Random Access Memory with Quantum Addressing), a hardware model that does not exist and faces severe engineering challenges \cite{ref18}.

\textit{Quantum walks and the heuristic/QRAQM barrier.} Structured search improvements arise from quantum walks \cite{ref14}, formalized by the MNRS framework \cite{ref15}. For subset-sum, Bernstein et al.\ reach $O(2^{0.241n})$ \cite{ref16} and Helm--May $O(2^{0.226n})$ \cite{ref17}---the strongest asymptotics known. Yet two caveats motivate our work: (i)~they assume \emph{Heuristic~2}, an unproven claim about walk-update costs that Bonnetain et al.\ showed to be mathematically unsound in general, recovering provable but weaker bounds ****\cite{bonnetain2020improved}****; and (ii)~they require QRAQM (quantum-addressable quantum memory), whose feasibility is heavily contested \cite{ref18,ref19}. The best ``quantum'' knapsack asymptotics are therefore simultaneously unproven and hardware-infeasible.

\textit{Closest prior work and our position.} Three works are nearest to ours. Montanaro's quantum B\&B \cite{ref24} is provable and QRAQM-free but \emph{generic}: it bounds a quantum walk on an abstract tree of size $T$ by $\tilde{O}(\sqrt{T}\,d)$ without analyzing any specific problem, the role of LP bounds, or the induced tree size for knapsack. The QTG of Wilkening et al.\ \cite{ref23} is knapsack-specific and gate-model, but feeds feasible-solution superpositions to a \emph{variational} (QAOA) routine and performs no LP-based variable fixing, inheriting QAOA's lack of guarantees. Bonnetain et al.\ ****\cite{bonnetain2020improved}**** restore provability to walk-based subset-sum yet still assume QRAQM. Our algorithm uniquely combines: (a)~\emph{exact} LP reduced-cost fixing with Montanaro's provable, QRAQM-free quantum B\&B specifically for knapsack, (b)~an analysis of the resulting LP-pruned tree size $T_{\text{LP}} \le T$, and (c)~computational spectral validation of the explicit walk operator on completed simulable trees. Table~\ref{tab:related} contrasts these properties.

\begin{table}[htbp]
\caption{Capability comparison with the closest prior quantum methods. The lower block lists capabilities that, to our knowledge, no prior method provides simultaneously.}
\label{tab:related}
\begin{center}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lcccc}
\toprule
\textbf{Capability} & \textbf{Mont.} & \textbf{QTG} & \textbf{Bonn.} & \textbf{Ours} \\
 & \cite{ref24} & \cite{ref23} & ****\cite{bonnetain2020improved}**** & \\
\midrule
Provable query reduction               & Yes & No\textsuperscript{\S} & Yes & \textbf{Yes} \\
Gate-model feasible (no QRAQM)         & Yes & Yes & No  & \textbf{Yes} \\
Knapsack-specific                      & No  & Yes & No  & \textbf{Yes} \\
\midrule
Exact LP variable fixing               & No  & No  & No  & \textbf{Yes} \\
Instance-adaptive$^\dagger$            & No  & No  & No  & \textbf{Yes} \\
Explicit walk spectral validation$^\ddagger$       & No  & No  & No  & \textbf{Yes} \\
Hardware demonstration                 & No  & No  & No  & \textbf{Yes} \\
\bottomrule
\multicolumn{5}{l}{\footnotesize Mont.: Montanaro B\&B; QTG: Quantum Tree Generator; Bonn.: Bonnetain et al.} \\
\multicolumn{5}{l}{\footnotesize $^\dagger$Query bound depends on the LP-pruned tree sizes encountered.}\\
\multicolumn{5}{l}{\footnotesize $^\ddagger$Explicit walk spectra and analytical detection criteria are evaluated computationally on completed simulable trees.} \\
\multicolumn{5}{l}{\footnotesize \textsuperscript{\S}Variational (QAOA): no performance guarantee.} \\
\end{tabular}
\end{center}
\end{table}

\begin{table}[htbp] \caption{Comparison of Knapsack/Subset-Sum Algorithms} \label{tab:comparison} \begin{center} \begin{tabular}{lcccc} \toprule \textbf{Algorithm} & \textbf{Reported Complexity Measure} & \textbf{Space} & \textbf{Prov.} & \textbf{QRAQM} \\ \midrule Horowitz--Sahni & $O(2^{n/2})$ & $O(2^{n/2})$ & Yes & N/A \\ Grover & $O(2^{n/2})$ & $O(n)$ & Yes & No \\ Bernstein et al. & $O(2^{0.241n})$ & $O(2^{0.241n})$ & No$^\dagger$ & Yes \\ Helm \& May & $O(2^{0.226n})$ & $O(2^{0.226n})$ & No$^\dagger$ & Yes \\ Montanaro B\&B & $\tilde{O}(\sqrt{T}\,d\log d)$ queries & $O(\text{poly})$ & Yes & No \\ QTG+AA & $O(\sqrt{N_f})$ & $O(\text{poly})$ & Yes & No \\ \textbf{Ours} & $O(\sqrt{T_{\max}}\,m\log m\log V_{\max})$ queries & $O(\text{poly})$ & \textbf{Yes} & \textbf{No} \\ \bottomrule \multicolumn{5}{l}{\footnotesize $^\dagger$Relies on Heuristic 2, shown unsound by ****\cite{bonnetain2020improved}****.} \\ \multicolumn{5}{l}{\footnotesize $T$: full B\&B tree. $T_{LP}$: LP-pruned tree ($T_{LP} \ll T$). $N_f$: feasible states. $m$: core size.} \end{tabular} \end{center} \end{table}

## ref1 
**PDF File:** `dantzig1957.pdf`

### Context 1
> \textit{Classical exact methods.} Dantzig's LP relaxation yields a closed-form fractional optimum and the tight Dantzig upper bound that remains the workhorse of exact knapsack solvers ****\cite{ref1}****.

### Context 2
> The LP relaxation of \eqref{eq:knapsack} permits fractional assignments $x_i \in [0,1]$. Its solution has a closed-form structure due to Dantzig ****\cite{ref1}****.


## ref2 
**PDF File:** `horowitz1974.pdf`

### Context 1
> Despite its simple formulation, the problem is NP-hard, and the best classical exact algorithm---the Horowitz--Sahni meet-in-the-middle approach---runs in $O(2^{n/2})$ time and space ****\cite{ref2}****.

### Context 2
> The Horowitz--Sahni meet-in-the-middle (MitM) algorithm splits the items into two halves and merges sorted partial sums, attaining $O(2^{n/2})$ time and space ****\cite{ref2}****---still the best \emph{provable} worst-case bound for exact 0/1 knapsack and the natural classical target for any quantum method.

### Context 3
> The Horowitz--Sahni algorithm ****\cite{ref2}**** partitions the $n$ items into two disjoint sets $A$ and $B$ with $|A| = |B| = n/2$. It enumerates all $2^{n/2}$ subsets of $A$, storing pairs $(w(S_A), v(S_A))$ for each subset $S_A \subseteq A$... It does the same for $B$. Then, for each subset $S_A$ of $A$, it finds the best compatible subset $S_B$ of $B$ satisfying $w(S_A) + w(S_B) \leq W$ using binary search on the sorted list of $B$-subsets. The total time and space are both $O(2^{n/2})$.


## ref4 
**PDF File:** `pisinger1999.pdf`

### Context 1
> Pisinger's \emph{core} concept is central to our approach: empirically only items whose efficiency lies near the LP split affect the optimum ****\cite{ref4}****, and reduced-cost variable fixing turns this observation into an \emph{exact} reduction.

### Context 2
> The core concept was introduced by Pisinger ****\cite{ref4}****, who showed empirically that $|C| \ll n$ for typical instances. Our algorithm exploits this structure theoretically.

### Context 3
> Given a lower bound $Z_{\text{LB}}$ (e.g., from a greedy solution), an item~$i$ with $x_i^{LP} = 1$ can be \textit{provably fixed} to~1 if removing it causes the LP upper bound to drop below $Z_{\text{LB}}$. Similarly, an item~$j$ with $x_j^{LP} = 0$ can be fixed to~0 if forcing it in causes the LP bound to drop below $Z_{\text{LB}}$. This technique, due to Pisinger~****\cite{ref4}****, is exact---no heuristic assumptions are involved.


## ref16 
**PDF File:** `bernstein2013.pdf`

### Context 1
> More sophisticated quantum approaches based on quantum walks have achieved better asymptotic complexities. Bernstein et al. \cite{ref16} achieved $O(2^{0.241n})$... However, these results rely on Heuristic~2... Furthermore, these algorithms require QRAQM...

### Context 2
> For subset-sum, Bernstein et al.\ reach $O(2^{0.241n})$ \cite{ref16} ... Yet two caveats motivate our work: (i)~they assume \emph{Heuristic~2}...


## ref17 
**PDF File:** `helm&may2018.pdf`

### Context 1
> ...and Helm and May \cite{ref17} further improved this to $O(2^{0.226n})$. However, these results rely on Heuristic~2...

### Context 2
> ...and Helm--May $O(2^{0.226n})$ \cite{ref17}---the strongest asymptotics known. Yet two caveats motivate our work: (i)~they assume \emph{Heuristic~2}...

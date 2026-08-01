# Multidimensional Knapsack (Table IV) Re-Run Results

## 1. Original Script Audit and Explicit Correction
- **Location**: `simulation/multidim_knapsack.py`
- **Original Parameters**: The original script looped over $n \in \{10, 14, 18\}$, averaging the results. It used only **8 trials** (`for seed in range(8)`) per configuration. 
- **Explicit Correction**: The original Table IV (values 0.28/0.51/0.72/0.83) was generated using `gen_multidim()`, which drew weights AND values independently and uniformly at random — i.e., UNCORRELATED instances — despite the paper's prose claiming "strongly correlated instances." **This was a mislabeling error in the original experiment, now corrected.**

## 1.5 Negative Control (Verification of Algorithm)
To ensure that the saturation to $\alpha=1.0$ for strongly correlated instances was not a bug in the multidimensional fixing implementation, a **negative control** was run using the corrected code (`multidim_knapsack_v2.py` logic) on UNCORRELATED instances at $d=2, n=24$.
- **Result**: For uncorrelated instances at $d=2$, the core ratio was **$\alpha = 0.713 \pm 0.124$** (min: 0.125, max: 1.000). 
- **Conclusion**: Phase 1 successfully fixes a significant fraction of variables for easier instance classes. The code functions correctly. The saturation to $\alpha = 1.0$ observed for strongly-correlated instances is a genuine mathematical finding about their hardness, not an algorithmic bug.

## 2. Surrogate Relaxation Claim Verification
**Claim**: Sorting items by per-constraint efficiencies yields provably valid upper bounds for reduced-cost fixing via the minimum of $d$ single-constraint Dantzig bounds.

**Derivation** (Valid):
1. Let $\mathcal{F}_d = \{ x \in [0, 1]^n \mid \sum_i w_{ij} x_i \le W_j \ \forall j \in \{1\dots d\} \}$ be the feasible region of the $d$-dimensional LP relaxation. 
2. Let $\mathcal{F}^{(k)} = \{ x \in [0, 1]^n \mid \sum_i w_{ik} x_i \le W_k \}$ be the feasible region of the single $k$-th constraint relaxation. Since $\mathcal{F}^{(k)}$ removes $d-1$ constraints, it is a strict superset of $\mathcal{F}_d$ ($\mathcal{F}_d \subseteq \mathcal{F}^{(k)}$).
3. The $k$-th Dantzig bound, $D_k$, is exactly the optimal value over $\mathcal{F}^{(k)}$. Because the maximum of an objective over a superset must be $\ge$ the maximum over the subset, $D_k \ge Z_{\text{LP}}^{(d)}$ for all $k$.
4. Therefore, $\min_k (D_k) \ge Z_{\text{LP}}^{(d)}$, making it a provably valid upper bound.

## 3. Re-Run Parameters
- **n**: 24
- **Trials**: 20 seeds per configuration.
- **Generation Method**: Formally extended "strongly correlated" instances. Weights are independent uniform $w_{ij} \sim U(1, 100)$. Values are tied to the average weight: $v_i = \lfloor \frac{1}{d} \sum_{j=1}^d w_{ij} \rfloor + 10$.
- **Script**: `simulation/multidim_knapsack_v2.py`
- **Classification**: MEASURED for re-run data.

## 4. Re-Run Results (Strongly Correlated)
- **d=1**: $\alpha = 0.958$ (std dev: 0.131) [min 0.46, max 1.00]
- **d=2**: $\alpha = 1.000$ (std dev: 0.000) [min 1.00, max 1.00]
- **d=3**: $\alpha = 1.000$ (std dev: 0.000) [min 1.00, max 1.00]
- **d=4**: $\alpha = 1.000$ (std dev: 0.000) [min 1.00, max 1.00]

The results confirm that strongly correlated multidimensional instances strongly resist variable fixing, saturating to $\alpha=1.0$ instantly at $d \ge 2$.

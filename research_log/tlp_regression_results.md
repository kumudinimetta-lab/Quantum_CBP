# T_LP Regression Analysis Results

**Dataset**: Existing 700-instance benchmark dataset from `benchmark_results_v5_hard.json` ($n \in \{12, 14, 16, 18, 20, 22, 24\}$, 20 seeds each across 5 classes).
**Recomputation**: The exact `w, v, cap` arrays for each instance were re-generated using the original seeds to recompute the exact LP bound (`Z_LP`) and exact optimal value (`Z*`) using DP. The gap was computed as `gap = Z_LP - Z*`.
**Handling Zeros**: 141 instances (all of `subset_sum` and a few others) had `gap = 0`. An epsilon of `1e-6` was added before log-transformation (`log_gap = np.log(gap + 1e-6)`). No instances had `T_full = 0`. All data is classified as MEASURED (for counts) and DERIVED (for coefficients/statistics).

## Final Model Forms Evaluated
1. **Pooled Model**: `log(T_full) ~ log(gap) + m` (and alternatives adding `n` and interaction).
2. **Per-Class Models**: `log(T_full) ~ log(gap) + m` individually per class.

## Correlation Matrix (Pooled)
|       |        m |       gap |         n |     log_T |
|:------|---------:|----------:|----------:|----------:|
| m     | 1.000000 | -0.329677 |  0.436542 |  0.603069 |
| gap   | -0.329677|  1.000000 | -0.125053 |  0.003810 |
| n     |  0.436542| -0.125053 |  1.000000 |  0.251392 |
| log_T |  0.603069|  0.003810 |  0.251392 |  1.000000 |

## Results: R² and Cross-Validation (5-Fold CV Out-of-Sample R²)

| Model Scope          | R²    | Adj. R² | CV R² (Mean ± Std) |
|----------------------|-------|---------|---------------------|
| Pooled (Base)        | 0.469 | 0.468   | 0.4602 ± 0.0666     |
| Pooled (+n)          | 0.473 | 0.470   | 0.4633 ± 0.0658     |
| Pooled (Interaction) | 0.530 | 0.528   | 0.5217 ± 0.0615     |
| Uncorrelated         | 0.627 | 0.621   | 0.5840 ± 0.0622     |
| Weakly Correlated    | 0.594 | 0.588   | 0.4787 ± 0.1629     |
| Strongly Correlated  | 0.601 | 0.595   | 0.5599 ± 0.0414     |
| Subset Sum           | 0.010 | 0.003   | -0.0744 ± 0.0678    |
| Inverse Strongly     | 0.583 | 0.577   | 0.5402 ± 0.1293     |

## Coefficients and 95% CIs (Base Form: log_T ~ log_gap + m)

| Model                | Term       | Coef    | P>\|t\| | [0.025, 0.975] |
|----------------------|------------|---------|---------|----------------|
| **Pooled**           | Intercept  | 3.1581  | 0.000   | [3.010, 3.307] |
|                      | log_gap    | 0.0629  | 0.000   | [0.052, 0.073] |
|                      | m          | 0.1255  | 0.000   | [0.115, 0.136] |
| **Uncorrelated**     | Intercept  | 3.2627  | 0.000   | [3.096, 3.429] |
|                      | log_gap    | -0.0038 | 0.919   | [-0.078, 0.071]|
|                      | m          | 0.1078  | 0.000   | [0.092, 0.123] |
| **Strongly Corr.**   | Intercept  | 2.1563  | 0.000   | [1.592, 2.720] |
|                      | log_gap    | 1.0091  | 0.000   | [0.795, 1.223] |
|                      | m          | 0.1186  | 0.000   | [0.086, 0.151] |
| **Subset Sum**       | (See Note) | -       | -       | -              |

*Note: The `subset_sum` class trivially has a gap of 0 for all instances (since $v_i = w_i$), causing extreme multicollinearity and making regression on `log_gap` statistically meaningless.*

## Verdict
The relationship between $T_{LP}$ and $(gap, m)$ is **highly class-dependent** and should not be characterized by a single pooled equation. While $m$ is a consistently strong positive predictor across valid classes, the integrality `gap` behaves erratically depending on instance structure. For `strongly_correlated` and `inverse_strongly` instances, larger gaps strongly predict larger trees (coefficient ~0.5 to 1.0, high significance). However, for `uncorrelated` instances, `gap` provides virtually zero predictive power ($p = 0.919$), and for `subset_sum`, the gap is identically zero making the model undefined. Therefore, any empirical claims must be scoped per-class; asserting a universal scaling law across all knapsack types based on these predictors would be misleading.

## Additional Clarifications

1. **Handling of Zero-Gap Instances**: Zero-gap instances (141 total, including all of subset_sum) were not dropped. They were epsilon-adjusted by adding exactly 1e-6 prior to the log transformation (log(gap + 1e-6)). This does not artificially distort the subset_sum ^2=0.010$ result; because *every* subset_sum instance had a gap of exactly 0, log_gap became a constant vector, meaning it mathematically could not explain any variance (leading to the singular matrix warning and near-zero ^2$).

2. **Recomputed {LP}$ Averages**: The recomputed average full-tree sizes for =24$ exactly align with the paper's existing claims:
   - **Uncorrelated (=24$)**: Recomputed = 69.35 | Paper = ~70
   - **Strongly Correlated (=24$)**: Recomputed = 3078.7 | Paper = ~3079
   This confirms the regression operates on identically the same underlying data/scaling behaviors as the rest of the text.

3. **Definition of Gap**: The gap variable is defined strictly as {LP} - Z^*$ (where ^*$ is the exact optimal value, computed here via an exact Dynamic Programming solver), rather than using the greedy lower bound {LB}$. Consequently, the coefficients represent sensitivity to the *true* LP integrality gap.

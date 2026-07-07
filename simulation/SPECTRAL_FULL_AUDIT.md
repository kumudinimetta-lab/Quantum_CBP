# Spectral Validation Full Adversarial Audit

## 1. Selection-Bias Audit (TREE_CAP and EMPTY_CORE)

Total Attempted Conditions: 1200 (600 marked, 600 unmarked)

### Full Status Taxonomy (sums to exactly 1200)
- COMPLETED_marked: 489
- COMPLETED_unmarked: 400
- TREE_CAP_marked: 74
- TREE_CAP_unmarked: 0
- EMPTY_CORE_seed_level (both marked/unmarked bypassed): 37 seeds (74 conditions)
- EMPTY_CORE_tree_level_marked: 0
- EMPTY_CORE_tree_level_unmarked: 163
- NUMERICAL_FAILURE_marked: 0
- NUMERICAL_FAILURE_unmarked: 0
- ASSERTION_FAILURE_seed_level: 0

### Pre-eigendecomposition Quantity Comparison (m)
- COMPLETED median $m$: 10.0 (IQR: 7.0)
- TREE_CAP median $m$: 16.0 (IQR: 4.0)

> [!WARNING]
> The spectral conclusions presented in the following sections apply strictly to trees satisfying $T_{\text{LP}} \le 2000$. These results do not empirically generalize to capped trees.

## 2. Unmarked Effective Spectral-Gap Inequality

Total Completed Unmarked Instances: 400

| $c$ | $x/N$ Satisfying Bound | 95% Clopper-Pearson CI | Max $R_c$ | Median $R_c$ (95% CI) |
| --- | --- | --- | --- | --- |
| 0.125 | 400/400 | [0.9908, 1.0000] | 0.000000 | 0.000000 [0.000000, 0.000000] |
| 0.25 | 400/400 | [0.9908, 1.0000] | 0.000000 | 0.000000 [0.000000, 0.000000] |
| 0.5 | 400/400 | [0.9908, 1.0000] | 0.000000 | 0.000000 [0.000000, 0.000000] |
| 1.0 | 400/400 | [0.9908, 1.0000] | 0.931573 | 0.812803 [0.803094, 0.823769] |
| 2.0 | 400/400 | [0.9908, 1.0000] | 0.250000 | 0.208430 [0.205827, 0.212050] |

### Unmarked Violations
No violations observed.

## 3. Marked Phase-Zero Weight Inequality

Total Completed Marked Instances: 489

| $\epsilon$ | $x/N$ Satisfying Bound | 95% Clopper-Pearson CI | Min $w_0$ | Median $w_0$ (95% CI) |
| --- | --- | --- | --- | --- |
| 1e-08 | 489/489 | [0.9925, 1.0000] | 0.500000 | 0.500000 [0.500000, 0.560010] |
| 1e-10 | 489/489 | [0.9925, 1.0000] | 0.500000 | 0.500000 [0.500000, 0.560010] |
| 1e-12 | 489/489 | [0.9925, 1.0000] | 0.500000 | 0.500000 [0.500000, 0.560010] |

### Marked Violations
No violations observed.

## 4. Analytical Phase-Estimation Acceptance Separation

### Descriptive Statistics
| Condition | Precision | Median $p_{\text{accept}}$ | Bootstrap 95% CI | IQR |
| --- | --- | --- | --- | --- |
| Marked | s-2 | 0.730600 | [0.723603, 0.739970] | 0.115812 |
| Marked | s-1 | 0.598620 | [0.589966, 0.608665] | 0.169457 |
| Marked | s0 | 0.517707 | [0.515338, 0.566443] | 0.175230 |
| Marked | s1 | 0.506129 | [0.505202, 0.554994] | 0.180947 |
| Unmarked | s-2 | 0.704332 | [0.696587, 0.712821] | 0.090775 |
| Unmarked | s-1 | 0.452287 | [0.433944, 0.473367] | 0.192762 |
| Unmarked | s0 | 0.031051 | [0.023644, 0.042515] | 0.099905 |
| Unmarked | s1 | 0.017134 | [0.014539, 0.019816] | 0.027675 |

### Paired Within-Tree Comparison ($s-1$ vs $s$)
- **Marked** ($N=489$): Median paired difference $\Delta = -0.002679$ (95% CI: [-0.003883, -0.001890]). Wilcoxon signed-rank test statistic $W = 0.0$, $p = 1.53e-79$.
- **Unmarked** ($N=400$): Median paired difference $\Delta = -0.387917$ (95% CI: [-0.396836, -0.379914]). Wilcoxon signed-rank test statistic $W = 0.0$, $p = 2.73e-67$.

## 5. Analytical Detection Criterion Agreement

- **Marked Agreement**: 489/489 (100.0%), 95% CI: [0.9925, 1.0000]
- **Unmarked Agreement**: 400/400 (100.0%), 95% CI: [0.9908, 1.0000]
- **Total Agreement**: 889/889 (100.0%), 95% CI: [0.9959, 1.0000]

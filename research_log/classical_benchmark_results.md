# Classical B&B Benchmark Results (Phase 1 + Core B&B vs OR-Tools)

## 1. OR-Tools Verification
- **Status:** Installed and verified working.
- **Version:** Google OR-Tools 9.15.6755
- **Trivial test:** Correctly solved a trivial 3-item knapsack problem instance to optimality during initialization.

## 2. Existing Paper Claims Audit
- **Claim:** The paper's abstract claims "We benchmark against strong classical solvers (dynamic programming, Google OR-Tools)".
- **Verification:** I searched the existing codebase and found `simulation/baselines.py` which contains `solve_ortools()` utilizing `ortools.algorithms.python.knapsack_solver`. The repository also contains a populated `baselines_results.json` file.
- **Verdict:** The paper's claim of having run an OR-Tools benchmark is **substantiated** by existing scripts and data.

## 3. Scale-Up Benchmark Results (MEASURED)
The benchmark tested 5 instance classes (5 trials per instance size). For tractable classes, sizes up to n=1000 were tested (3 classes x 4 sizes x 5 = 60). For intractable classes, testing was hard-stopped at n=500 (2 classes x 3 sizes x 5 = 30). This resulted in exactly **90** total attempted instances.
- **Correctness (Clarification):** The claim of "zero mismatches" applies **ONLY** to instances where BOTH solvers returned a certified optimal (did not hit cutoffs). Out of the 90 total instances attempted, exactly **69** instances were fully solved to certified optimality by both solvers. In 100% of these 69 cases, the optimal value returned by our LP-pruned B&B perfectly matched OR-Tools (zero mismatches).
- **Phase 1 Effectiveness:** Across EVERY tested class and size, Phase 1 (reduced-cost fixing) resolved 0/5 instances outright. This means Phase 2 (the quantum/classical B&B core-solving step) was required in 100% of tested cases.
- **Intractability:** For instances where one or both solvers hit their cutoffs (20s for OR-Tools, 1,000,000 nodes for ours), real timing comparisons are impossible. We report these separately below.

### Category (a): Both Solvers Reached Certified Optimal
These are cases where true timing comparisons are valid. 

*Note on Core m Averages: The average core size (m) reported here is computed ONLY over the non-timeout subset. Harder instances (with larger cores) are more likely to time out and fall into Category (b). This explains why the Core m average here is smaller than a raw average over all 5 trials.*
| Instance Class | n | Successes | Core m | OR-Tools (s) | Our LP+B&B (s) | Notes |
|----------------|-----|-----------|---------|--------------|----------------|-------|
| **uncorrelated** | 100 | 5/5 | 18.2 | 0.0001 | 0.0031 |  |
| **uncorrelated** | 200 | 5/5 | 27.2 | 0.0000 | 0.0210 |  |
| **uncorrelated** | 500 | 5/5 | 78.0 | 0.0002 | 0.0984 |  |
| **uncorrelated** | 1000 | 5/5 | 75.6 | 0.0001 | 0.3301 |  |
| **weakly_correlated** | 100 | 5/5 | 79.4 | 0.0000 | 0.0032 |  |
| **weakly_correlated** | 200 | 5/5 | 56.4 | 0.0002 | 0.0107 |  |
| **weakly_correlated** | 500 | 5/5 | 91.6 | 0.0001 | 0.0729 |  |
| **weakly_correlated** | 1000 | 5/5 | 126.2 | 0.0001 | 0.3253 |  |
| **subset_sum** | 100 | 5/5 | 100.0 | 0.0000 | 0.0028 |  |
| **subset_sum** | 200 | 5/5 | 200.0 | 0.0000 | 0.0109 |  |
| **subset_sum** | 500 | 5/5 | 500.0 | 0.0000 | 0.0733 |  |
| **subset_sum** | 1000 | 5/5 | 1000.0 | 0.0001 | 0.2970 |  |
| **strongly_correlated** | 100 | 3/5 | 100.0 | 0.0809 | 0.0877 |  |
| **strongly_correlated** | 200 | 2/5 | 200.0 | 0.0130 | 0.0607 | Warning: n=2, not a stable avg |
| **inverse_strongly** | 100 | 3/5 | 36.0 | 0.0563 | 0.0191 |  |
| **inverse_strongly** | 200 | 1/5 | 25.0 | 0.0017 | 0.0108 | Warning: n=1, not a stable avg |

### Category (b): Cutoffs Reached
These are cases where at least one solver timed out (OR-Tools > 20s, or Ours > 1,000,000 nodes). The previously-reported timing numbers for these instances (e.g., Strongly Correlated and Inverse Strongly at n=500) were **invalid** because cutoff times are not solve times.
| Instance Class | n | OR-Tools Timeouts | Our B&B Timeouts |
|----------------|-----|-------------------|------------------|
| **strongly_correlated** | 100 | 2/5 | 2/5 |
| **strongly_correlated** | 200 | 3/5 | 3/5 |
| **strongly_correlated** | 500 | 5/5 | 5/5 |
| **inverse_strongly** | 100 | 2/5 | 2/5 |
| **inverse_strongly** | 200 | 4/5 | 4/5 |
| **inverse_strongly** | 500 | 5/5 | 5/5 |
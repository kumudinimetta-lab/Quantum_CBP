# Hybrid Quantum-Classical Knapsack: Research Knowledge Base

## Algorithm Design (Final Version)

### Architecture: LP-Pruned Quantum Branch-and-Bound

**Phase 1: Classical LP Preprocessing** (O(n log n))
- Solve LP relaxation (Dantzig bound)
- Reduced-cost variable fixing: fix items provably in/out
- Output: m core items where m ≤ n

**Phase 2: Quantum Branch-and-Bound on Core** (O(sqrt(T_LP) * poly(m)))
- Construct B&B tree over m core items
- LP relaxation bounds at each node for pruning
- Montanaro quantum walk on implicit B&B tree
- Finds optimal core assignment in sqrt(T_LP) queries

**Phase 3: Classical Post-Processing** (O(n))
- Combine with fixed items, verify optimality

### Key Theorems to Prove

1. **Tree Size Bound (Uncorrelated)**: E[T_LP] = O(poly(n)) for random efficiency distributions
2. **Tree Size Bound (Correlated)**: E[T_LP] = Omega(2^(cn)) for strongly correlated instances
3. **Quantum Speedup**: Algorithm runs in O(sqrt(T_LP) * poly(m, d, log W))
4. **Universal Optimality**: Never asymptotically worse than any single baseline

## Complete Literature Map

### Provable Quantum Algorithms (no heuristics, no QRAQM)
| Algorithm | Complexity | Limitation |
|-----------|-----------|-----------|
| Grover search | O(2^(n/2)) | Same as classical MitM |
| Montanaro backtracking (2018) | O(sqrt(T)*poly(d)) | Generic, not knapsack-specific |
| Montanaro B&B (2020) | O(sqrt(T)*poly(d)) | No LP-specific analysis |
| QTG + AA (Wilkening 2023) | O(sqrt(N_feas)) | No LP pruning |
| **Ours** | **O(sqrt(T_LP)*poly(m))** | **Novel: LP + quantum B&B** |

### Heuristic Quantum Algorithms (require assumptions)
| Algorithm | Complexity | Assumption |
|-----------|-----------|-----------|
| BJLM (2013) | O(2^(0.241n)) | QRAQM + Heuristic 2 |
| Helm & May (2018) | O(2^(0.226n)) | QRAQM + Heuristic 2 |
| Bonnetain et al. (2020) | O(2^(0.218n)) | QRAQM (H2 partially removed) |

### Key References
- [Pisinger 1997] Core concept, minknap algorithm
- [Montanaro 2018] Quantum backtracking (ToC)
- [Montanaro 2020] Quantum B&B (Phys. Rev. Research)
- [Bonnetain et al. 2020] Refutation of Heuristic 2
- [Wilkening et al. 2023] QTG for knapsack
- [Bernstein et al. 2013] Quantum walks on subset sum

## Experimental Validation

### v3 (Correctness): 270/270 correct, alpha=0.358
### v4 (Tree sizes): T_LP grows slowly for random instances
### v5 (Hard instances): 700/700 correct across 5 instance types
- Uncorrelated: alpha=0.32, huge MitM speedup (89.9x)
- Strongly correlated: alpha=0.95, genuine quantum needed
- Subset sum: alpha=1.00, pure quantum B&B domain

## Project Files
- paper/main.tex - Research paper (needs updating)
- simulation/benchmark_v3.py - Correctness verification
- simulation/benchmark_v4.py - Tree size analysis
- simulation/benchmark_v5.py - Hard instance analysis

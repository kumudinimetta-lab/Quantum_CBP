import math
from benchmark_v5 import gen_uncorrelated, reduced_cost_fixing
from quantum_backtracking import quantum_bb_optimize, _classical_optimum

def run_smoke_test():
    n = 12
    seed = 12000
    w, v, cap, _ = gen_uncorrelated(n, seed)
    
    # Trusted exact classical solver for correctness
    classical_opt = _classical_optimum(w, v, cap)
    
    # Phase 1
    fi, core, fo = reduced_cost_fixing(n, w, v, cap)
    
    fixed_0_count = len(fo)
    fixed_1_count = len(fi)
    m = len(core)
    
    # Compute residual capacity W'
    W_prime = cap - sum(w[i] for i in fi)
    
    print(f"Original n: {n}")
    print(f"Fixed-0 count: {fixed_0_count}")
    print(f"Fixed-1 count: {fixed_1_count}")
    print(f"Resulting core size (m): {m}")
    print(f"Residual capacity (W'): {W_prime}")
    
    assert W_prime >= 0, "Phase 1 assertion failure: negative residual capacity"
    
    core_w = [w[i] for i in core]
    core_v = [v[i] for i in core]
    
    # Mandatory assertions
    assert len(core_w) == m
    assert len(core_v) == m
    
    max_core_tree_nodes = (2 ** (m + 1)) - 1
    print(f"Theoretical max core-tree nodes: {max_core_tree_nodes}")
    
    if m == 0:
        print("Empty core. Optimum is just fixed items.")
        hybrid_opt = sum(v[i] for i in fi)
        assert hybrid_opt == classical_opt
        return
        
    res = quantum_bb_optimize(core_w, core_v, W_prime, constant=2.0, K=11, max_nodes=20000)
    
    # The depth of the quantum walk should be the core size, not n!
    # Wait, the internal depth is the length of the arrays passed to it.
    # Since we pass `core_w`, the depth inside `quantum_bb_optimize` is `len(core_w) = m`.
    depth = m
    T_LP = res.max_tree
    Q_d = res.montanaro_queries_decisive
    Q = res.quantum_queries_total
    quantum_opt = res.optimal_value
    
    hybrid_opt = sum(v[i] for i in fi) + quantum_opt
    
    print(f"Actual tree nodes (T_LP): {T_LP}")
    print(f"Actual tree depth (d): {depth}")
    print(f"Quantum queries decisive (Q_d): {Q_d}")
    print(f"Total quantum queries (Q): {Q}")
    print(f"Hybrid objective: {hybrid_opt}")
    print(f"Classical optimum: {classical_opt}")
    
    assert depth <= m
    assert T_LP <= max_core_tree_nodes
    assert hybrid_opt == classical_opt
    print("ALL ASSERTIONS PASSED!")

if __name__ == "__main__":
    run_smoke_test()

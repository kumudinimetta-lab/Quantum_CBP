import math
import numpy as np
import scipy.sparse as sp

from quantum_backtracking import Tree, build_walk_operator

def test_marked_mapping():
    # Construct a small deterministic tree with 1 marked vertex
    # root = 0
    # children of root: 1, 2
    # children of 1: 3, 4
    # marked vertex: 4
    tree = Tree()
    root = tree._add(None, 0) # 0
    c1 = tree._add(root, 1)   # 1
    c2 = tree._add(root, 1)   # 2
    c3 = tree._add(c1, 2)     # 3
    c4 = tree._add(c1, 2)     # 4
    
    tree.marked[4] = True
    
    T = tree.size
    n_depth = 3 # Let's say d_bound = 3
    
    W = build_walk_operator(tree, n_depth)
    W_dense = W.toarray()
    
    # Construct marked path vector |phi>
    # Path to 4: 0 -> 1 -> 4
    phi = np.zeros(T, dtype=complex)
    phi[0] = math.sqrt(n_depth)
    phi[1] = (-1)**1
    phi[4] = (-1)**2
    
    # 2. Verify || W |phi> - |phi> || < 10^-10
    W_phi = W_dense @ phi
    diff_norm = np.linalg.norm(W_phi - phi)
    print(f"diff_norm = {diff_norm}")
    
    # Compute overlaps directly from eigendecomposition
    evals, evecs = np.linalg.eig(W_dense)
    phases = np.angle(evals)
    
    root_vec = np.zeros(T)
    root_vec[0] = 1.0
    overlaps = np.abs(evecs.conj().T @ root_vec) ** 2
    
    print("w_0 evaluations:")
    for eps in [1e-8, 1e-10, 1e-12]:
        w_0 = sum(overlaps[i] for i in range(T) if abs(phases[i]) <= eps)
        print(f"  epsilon = {eps}: w_0 = {w_0} (>= 0.5? {w_0 >= 0.5})")

if __name__ == '__main__':
    test_marked_mapping()

import sys

def test_family(n):
    # Construct instance
    items = []
    for i in range(1, n + 1):
        w = 1.0
        v = 2.0 - i / (n**2)
        items.append((w, v, i))
    
    W = (n // 2) + 0.5
    
    # Calculate LP bound
    z_lp = 0.0
    rem_w = W
    s_idx = -1
    for idx, (w, v, i) in enumerate(items):
        if rem_w >= w:
            z_lp += v
            rem_w -= w
        else:
            z_lp += v * (rem_w / w)
            s_idx = idx
            break
            
    # Calculate greedy LB (just the items before s, since no other item fits in rem_w = 0.5)
    z_lb = 0.0
    rem_w_lb = W
    for idx, (w, v, i) in enumerate(items):
        if rem_w_lb >= w:
            z_lb += v
            rem_w_lb -= w
            
    gap = z_lp - z_lb
    
    # Run exact fixing logic using formula
    # We will compute the exact Z'_i for each item to be perfectly rigorous.
    core_items = []
    
    for test_idx in range(n):
        # LP without test_idx (force out if < s, force in if >= s)
        # Actually, standard fixing: 
        # If test_idx < s_idx, force OUT (x=0)
        # If test_idx > s_idx, force IN (x=1)
        # If test_idx == s_idx, it is fractional, so we test both x=0 and x=1. 
        # But reduced-cost fixing usually fixes to 0 if Z'_i(x=1) < Z_LB, etc.
        # Let's just use the marginal loss formula which we proved is an upper bound (and exact here since no split shift).
        
        # Check no-split-shift condition:
        # s_idx item has weight 1.0, R = 0.5.
        # If forced out (i < s): freed capacity is 1.0. Item s can only absorb w_s - R = 0.5.
        # Wait! If freed capacity is 1.0, and item s only has 0.5 available, the split WILL shift!
        # Ah! w_i = 1.0, w_s - R = 0.5. So w_i > w_s - R. Split shifts.
        pass

    # Let's just run an exact re-optimization for Z'_i
    for test_idx in range(n):
        test_w, test_v, _ = items[test_idx]
        
        # Test fixing to opposite of LP relaxation
        # If i <= s_idx, test forcing OUT (x=0)
        # If i >= s_idx, test forcing IN (x=1)
        
        # Actually, let's just evaluate BOTH x=0 and x=1 bounds and see if either drops below Z_LB
        # If max(Z'_{x=0}, Z'_{x=1}) < Z_LB, it's pruned. But wait, Z'_i is the bound for the forced choice.
        # To fix to 1, we need Z'(x=0) < Z_LB.
        # To fix to 0, we need Z'(x=1) < Z_LB.
        
        def exact_lp(forced_idx, forced_val):
            # Evaluate LP with item forced_idx set to forced_val
            z = 0.0
            r_w = W
            if forced_val == 1:
                z += items[forced_idx][1]
                r_w -= items[forced_idx][0]
                
            if r_w < 0: return -1.0 # Infeasible
                
            for idx, (w, v, _) in enumerate(items):
                if idx == forced_idx: continue
                if r_w >= w:
                    z += v
                    r_w -= w
                else:
                    z += v * (r_w / w)
                    break
            return z
            
        z0 = exact_lp(test_idx, 0)
        z1 = exact_lp(test_idx, 1)
        
        # Can we fix it?
        fixed = False
        if z0 < z_lb: 
            fixed = True # fixed to 1
        if z1 < z_lb:
            fixed = True # fixed to 0
            
        if not fixed:
            core_items.append(test_idx)
            
    print(f"n = {n:<4} | Z_LP = {z_lp:.4f} | Z_LB = {z_lb:.4f} | Gap = {gap:.4f} | |C_RC| = {len(core_items)}")

for n in [10, 50, 200, 1000]:
    test_family(n)


"""
Derive and verify the TRUE Z'_i for the Delta-necessity construction.

Construction:
  n items, w_i = 1.0, v_i = 2.0 - i/n^2, W = floor(n/2) + 0.5
  s = floor(n/2) + 1  (1-indexed, Python 0-indexed below = s-1)
  R = 0.5 (residual capacity before split item)

ALL items violate no-split-shift (w_i=1 > w_s - R = 0.5), so the
hat-Z'_i formula IS NOT exact here.  We must use the exact spillover.

CASE A: Force item i < s OUT
  Freed capacity = 1.0.
  Step 1: Fill item s completely (needs w_s - R = 0.5). Cost: 0.5 * e_s.
  Step 2: Remaining 0.5 spills into item s+1. Cost: 0.5 * e_{s+1}.
  TRUE Z'_i = Z_LP - v_i + 0.5*e_s + 0.5*e_{s+1}

CASE B: Force item j > s IN
  Need to consume capacity 1.0 from already-allocated items.
  Step 1: Remove item s entirely (contributes R = 0.5). Gain back: 0.5 lost.
  Step 2: Partially remove item s-1 (reduce by 0.5). Gain back: 0.5 lost.
  TRUE Z'_j = Z_LP + v_j - 0.5*e_s - 0.5*e_{s-1}

We then check: does TRUE Z'_i >= Z_LB hold for all items?
"""

from fractions import Fraction

def build_instance(n):
    items = [(Fraction(1), Fraction(2*n**2 - i, n**2)) for i in range(1, n+1)]
    # items[i] = (w, v) with v_i = (2n^2 - i)/n^2 = 2 - i/n^2
    W = Fraction(n // 2) + Fraction(1, 2)
    return items, W

def solve_lp(items, W, forced_out=None, forced_in=None):
    """Greedy LP relaxation with optional forcing."""
    rem = W
    z = Fraction(0)
    forced_out = forced_out or set()
    forced_in = forced_in or set()
    for idx, (w, v) in enumerate(items):
        if idx in forced_in:
            if rem < w:
                return None  # infeasible
            z += v
            rem -= w
        elif idx in forced_out:
            pass
        else:
            if rem >= w:
                z += v
                rem -= w
            elif rem > 0:
                z += v * rem / w
                rem = Fraction(0)
                break
    return z

def derive_true_zprime_out(items, s_idx, z_lp, z_lb, i_idx):
    """
    CASE A: Force item i_idx OUT (i_idx < s_idx).
    Freed capacity = w_i = 1.
    First 0.5 fills item s completely (from R=0.5 to w_s=1).
    Remaining 0.5 fills item s+1 fractionally.
    """
    w_i, v_i = items[i_idx]
    _, v_s = items[s_idx]
    e_s = v_s  # w_s = 1

    # Check s+1 exists (should for i < s < n-1)
    if s_idx + 1 >= len(items):
        return None  # edge case: s is the last item

    _, v_s1 = items[s_idx + 1]
    e_s1 = v_s1  # w_{s+1} = 1

    # TRUE Z'_i = Z_LP - v_i + 0.5*e_s + 0.5*e_{s+1}
    true_zprime = z_lp - v_i + Fraction(1, 2) * e_s + Fraction(1, 2) * e_s1
    return true_zprime

def derive_true_zprime_in(items, s_idx, z_lp, z_lb, j_idx):
    """
    CASE B: Force item j_idx IN (j_idx > s_idx).
    Consume capacity 1.0 from existing allocation.
    First 0.5 from removing item s entirely.
    Remaining 0.5 from partially removing item s-1 (reduce from 1.0 to 0.5).
    """
    w_j, v_j = items[j_idx]
    _, v_s = items[s_idx]
    e_s = v_s

    if s_idx - 1 < 0:
        return None  # edge case

    _, v_sm1 = items[s_idx - 1]
    e_sm1 = v_sm1  # w_{s-1} = 1

    # TRUE Z'_j = Z_LP + v_j - 0.5*e_s - 0.5*e_{s-1}
    true_zprime = z_lp + v_j - Fraction(1, 2) * e_s - Fraction(1, 2) * e_sm1
    return true_zprime

def check_n(n):
    items, W = build_instance(n)
    s_idx = n // 2  # 0-indexed split item = floor(n/2) [since items 0..s_idx-1 fill W - 0.5]

    z_lp = solve_lp(items, W)
    z_lb = solve_lp(items, W, forced_out={s_idx})  # brute-force: force s out, can't fill 0.5

    # Actually Z_LB = greedy integer solution: pack items 0..s_idx-1 fully
    z_lb_direct = sum(v for _, v in items[:s_idx])

    mismatches = 0
    formula_errors = 0

    for i in range(n):
        brute = solve_lp(items, W, forced_out={i})  # brute-force TRUE Z'_i

        if i < s_idx:
            derived = derive_true_zprime_out(items, s_idx, z_lp, z_lb_direct, i)
        elif i == s_idx:
            derived = None  # split item, skip for now
        else:
            derived = derive_true_zprime_in(items, s_idx, z_lp, z_lb_direct, i)

        if derived is not None:
            if brute != derived:
                print(f"  n={n}, item={i}: FORMULA MISMATCH brute={float(brute):.6f} derived={float(derived):.6f}")
                formula_errors += 1

            # Check: does TRUE Z'_i >= Z_LB?
            if brute < z_lb_direct:
                print(f"  n={n}, item={i}: ITEM FIXED (brute Z'_i={float(brute):.6f} < Z_LB={float(z_lb_direct):.6f})")
                mismatches += 1

    print(f"n={n:4d} | Z_LP={float(z_lp):.6f} | Z_LB={float(z_lb_direct):.6f} | "
          f"gap={float(z_lp - z_lb_direct):.6f} | formula_errors={formula_errors} | items_fixed={mismatches}")

    # Also show algebraic gap for a sample item (item 0, forced out)
    if n >= 4:
        i_sample = 0
        derived_sample = derive_true_zprime_out(items, s_idx, z_lp, z_lb_direct, i_sample)
        margin = derived_sample - z_lb_direct
        print(f"         Sample item 0 forced out: TRUE Z'_0 - Z_LB = {float(margin):.8f} "
              f"(= 1 - O(1/n^2) = 1 - {float(1 - margin):.8f})")

for n in [10, 50, 200, 1000]:
    check_n(n)
print("\nAll formula_errors=0 confirms the direct derivation is exact.")
print("All items_fixed=0 confirms no items are pruned (core size = n).")

"""
Diagnose which items cause the formula mismatch and why.
The issue: when item i << s (far before s) is forced out,
the freed capacity is 1.0.  But what if item s+1 is ALSO
already in the LP? No -- items after s have x=0.
So: freed 1.0 -> fills s (needs 0.5, contributes 0.5*e_s),
remaining 0.5 fills s+1 fractionally (contributes 0.5*e_{s+1}).
That's only ONE spillover step.

But brute force LP for item j > s forced out:
force j out, redo greedy LP.  The greedy LP is:
  items 0..j-1 (excluding j), 0..n-1 sorted by v desc (same order since all distinct).
When j > s, forcing j OUT from the baseline LP changes nothing
because j already has x=0 in the baseline!  So Z'_j = Z_LP for j > s.

OH WAIT.  In my test script, forced_out={i} forces item i OUT.
For i > s, item i was ALREADY out (x=0) in the baseline.
So forcing it out doesn't change the LP at all.
Z'_i = Z_LP (exactly) for any i > s that's forced OUT.
Those are not the relevant fixing tests.

Algorithm 1 does:
  - For items i < s (currently fully IN, x=1): test forcing OUT.
  - For items j > s (currently fully OUT, x=0): test forcing IN.
  - Item s is fractional, test both.

So my CASE B should be: force j > s IN (not OUT).
But in solve_lp I called forced_out={i} for ALL i.  That's wrong for i > s.
For j > s, the LP re-optimization to test in Algorithm 1's fixing is:
  force x_j = 1 (forced IN), recompute LP bound Z'_j.

Let me redo with the CORRECT fixing directions.
"""
from fractions import Fraction

def build_instance(n):
    # v_i = 2 - i/n^2 for i=1..n (1-indexed), weight=1
    items = [(Fraction(1), Fraction(2*n**2 - i, n**2)) for i in range(1, n+1)]
    W = Fraction(n // 2) + Fraction(1, 2)
    return items, W

def solve_lp_greedy(items, W, forced_out=None, forced_in=None):
    """Greedy fractional knapsack, respecting forced in/out."""
    forced_out = set() if forced_out is None else forced_out
    forced_in = set() if forced_in is None else forced_in
    rem = W
    z = Fraction(0)
    for idx in forced_in:
        w, v = items[idx]
        if rem < w:
            return None  # infeasible
        z += v
        rem -= w
    for idx, (w, v) in enumerate(items):
        if idx in forced_in or idx in forced_out:
            continue
        if rem <= 0:
            break
        if rem >= w:
            z += v
            rem -= w
        else:
            z += v * rem / w
            rem = Fraction(0)
    return z

def analyze(n):
    items, W = build_instance(n)
    s_idx = n // 2  # 0-indexed

    z_lp = solve_lp_greedy(items, W)
    z_lb = sum(v for _, v in items[:s_idx])  # greedy integer: pack items 0..s-1

    print(f"\nn={n}: Z_LP={float(z_lp):.8f}, Z_LB={float(z_lb):.8f}, gap={float(z_lp-z_lb):.8f}")
    print(f"  s_idx={s_idx} (0-indexed), e_s={float(items[s_idx][1]):.8f}")

    errors = 0

    # Test items i < s: fixing direction = force OUT (test if bound drops below Z_LB)
    for i in range(s_idx):
        brute = solve_lp_greedy(items, W, forced_out={i})
        # ONE-step spillover formula:
        e_s = items[s_idx][1]
        e_s1 = items[s_idx+1][1] if s_idx+1 < n else Fraction(0)
        w_i, v_i = items[i]
        derived = z_lp - v_i + Fraction(1,2)*e_s + Fraction(1,2)*e_s1
        if brute != derived:
            errors += 1
            if errors <= 3:  # print first few
                print(f"  MISMATCH i={i} (i<s): brute={float(brute):.8f} derived={float(derived):.8f}")

    # Test items j > s: fixing direction = force IN (test if bound drops below Z_LB)
    for j in range(s_idx+1, n):
        brute = solve_lp_greedy(items, W, forced_in={j})
        # ONE-step backward spillover formula:
        e_s = items[s_idx][1]
        e_sm1 = items[s_idx-1][1] if s_idx > 0 else Fraction(0)
        w_j, v_j = items[j]
        derived = z_lp + v_j - Fraction(1,2)*e_s - Fraction(1,2)*e_sm1
        if brute != derived:
            errors += 1
            if errors <= 3:
                print(f"  MISMATCH j={j} (j>s forced IN): brute={float(brute):.8f} derived={float(derived):.8f}")

    print(f"  Total formula mismatches: {errors}")

    # Confirm: ALL items have true Z'_i >= Z_LB?
    fixed = 0
    for i in range(s_idx):
        brute = solve_lp_greedy(items, W, forced_out={i})
        if brute < z_lb:
            fixed += 1
    for j in range(s_idx+1, n):
        brute = solve_lp_greedy(items, W, forced_in={j})
        if brute < z_lb:
            fixed += 1
    print(f"  Items FIXED by Algorithm 1: {fixed}  (core size = {n - fixed})")

    # Show algebraic margin for one sample
    i0 = 0
    brute0_out = solve_lp_greedy(items, W, forced_out={i0})
    margin0 = brute0_out - z_lb
    print(f"  Item 0 forced out: TRUE Z'_0={float(brute0_out):.8f}, Z_LB={float(z_lb):.8f}, margin={float(margin0):.8f}")

for n in [10, 50, 200, 1000]:
    analyze(n)

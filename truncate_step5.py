STEP5 = r"""

---

### Step 5: Necessity of the Delta-Spacing Assumption

**Proposition (Necessity of Delta).** Proposition 2's dependence on Delta is necessary:
no core-size bound of the form |C_RC| <= f(Z_LP - Z_LB) can hold without some
density or minimum-spacing assumption on item efficiencies.

**IMPORTANT — the hat-formula does NOT apply here.**
The Monotonicity Lemma (Steps 1.5–2) gives Z'_i <= hat{Z}'_i (the formula is an
UPPER bound on the true LP value). In this construction every item violates the
no-split-shift condition (w_i = 1 > w_s - R = 0.5), so hat{Z}'_i is not exact.
Showing hat{Z}'_i > Z_LB says nothing about whether the TRUE Z'_i exceeds Z_LB
(the inequality goes the wrong way). The proof below derives the TRUE Z'_i from
the exact LP re-optimisation.

---

**Construction.** For any n >= 2:
- Items: n items, 1-indexed. w_i = 1 for all i; v_i = 2 - i/n^2.
- Capacity: W = floor(n/2) + 1/2.
- Items are already sorted by decreasing efficiency since v_i is strictly decreasing.

Let s = floor(n/2) + 1 (1-indexed). Baseline LP:
- Items 1..s-1 fully packed (consuming floor(n/2) capacity).
- Residual capacity R = 1/2. Item s packed at R/w_s = 1/2.
- Items s+1..n have x = 0.

  Z_LP = sum_{j=1}^{s-1} v_j + (1/2)*v_s
  Z_LB = sum_{j=1}^{s-1} v_j   (greedy; remaining 1/2 cannot fit any weight-1 item)
  Z_LP - Z_LB = (1/2)*v_s = (1/2)*(2 - s/n^2) -> 1 as n -> infinity

The gap is bounded (approaches 1 from below) and does NOT grow with n.

---

**Case A — Force item i < s OUT** (Algorithm 1: test whether bound drops below Z_LB):

When x_i = 0, capacity w_i = 1 is freed. Since w_s - R = 1/2, the first 1/2 unit
fills item s to full inclusion. The remaining 1/2 then fills item s+1 fractionally
(w_{s+1} = 1). This is a single-step split shift.

  TRUE Z'_i = Z_LP - v_i + (1/2)*e_s + (1/2)*e_{s+1}
             = Z_LP - v_i + (1/2)*(v_s + v_{s+1})

[Verified EXACT against brute-force rational LP in derive_step5_v2.py: zero
formula mismatches at all tested n. Proof that it is exact: freed capacity 1
splits into two half-unit segments, each filling the next item in the greedy
order, and no further spillover occurs because only 1/2 reaches each step.]

Now compute Z'_i - Z_LB directly:

  Z'_i - Z_LB = (Z_LP - Z_LB) - v_i + (1/2)*(v_s + v_{s+1})
              = (1/2)*v_s - v_i + (1/2)*(v_s + v_{s+1})
              = v_s - v_i + (1/2)*v_{s+1}

Substituting v_k = 2 - k/n^2:

  v_s - v_i = (i - s)/n^2   [negative since i < s, but we subtract so contributes positively]

Wait, more carefully: v_s - v_i = (2 - s/n^2) - (2 - i/n^2) = (i - s)/n^2 <= 0 since i < s.

  (1/2)*v_{s+1} = 1 - (s+1)/(2n^2)

  Z'_i - Z_LB = (i - s)/n^2 + 1 - (s+1)/(2n^2)
              = 1 - [(s - i)/n^2 + (s+1)/(2n^2)]
              = 1 - [2(s-i) + (s+1)] / (2n^2)

Since i >= 1 and s = floor(n/2)+1:
  2(s-i) + (s+1) <= 2(s-1) + (s+1) = 3s - 1 <= 3*(n/2 + 1) - 1 = 3n/2 + 2

And 2n^2 >= 3n for n >= 2 (since 2n >= 3 for n >= 2).  Actually 2n^2 > 3n/2 + 2
for n >= 2 (at n=2: 8 > 5).  Therefore:

  Z'_i - Z_LB >= 1 - (3n/2 + 2)/(2n^2) = 1 - 3/(4n) - 1/n^2 > 0   for all n >= 2.

Item i < s is NOT fixed for any n >= 2.

---

**Case B — Force item j > s IN** (Algorithm 1: test whether bound drops below Z_LB):

When x_j = 1, capacity w_j = 1 must be reclaimed. Item s currently contributes
R = 1/2; removing it entirely frees 1/2. The remaining 1/2 needed is taken from
item s-1 (reducing its allocation from 1 to 1/2):

  TRUE Z'_j = Z_LP + v_j - (1/2)*e_s - (1/2)*e_{s-1}
             = Z_LP + v_j - (1/2)*(v_s + v_{s-1})

[Also zero formula mismatches in derive_step5_v2.py.]

  Z'_j - Z_LB = (Z_LP - Z_LB) + v_j - (1/2)*(v_s + v_{s-1})
              = (1/2)*v_s + v_j - (1/2)*(v_s + v_{s-1})
              = v_j - (1/2)*v_{s-1}

Substituting:

  v_j - (1/2)*v_{s-1} = (2 - j/n^2) - (1/2)*(2 - (s-1)/n^2)
                       = 1 - [2j - (s-1)] / (2n^2)

Since j <= n and s >= 2: 2j - (s-1) <= 2n - 1 < 2n.
And 2n^2 > 2n for n >= 2.  Therefore:

  Z'_j - Z_LB >= 1 - 2n/(2n^2) = 1 - 1/n > 0   for all n >= 2.

Item j > s is NOT fixed for any n >= 2.

---

**The actual mechanism:**
All n item efficiencies are packed into a window of width (n-1)/n^2 < 1/n around
e_s. When a split shift occurs (as it always does here because w_i = 1 > 0.5 = w_s - R),
the freed or consumed capacity lands on the immediately adjacent item, whose efficiency
differs from e_s by at most 1/n^2. The true marginal cost of each fixing decision is
therefore O(1/n^2), far below the O(1) LP gap. This is what prevents any item from
being fixed.

The minimum spacing in this family is Delta_n = min_{i != j} |e_i - e_j| = 1/n^2.
As n -> infinity, Delta_n -> 0 and the Proposition 2 bound diverges: the denominator
w_min * Delta_n = 1/n^2 -> 0, so the bound |C_RC| <= floor(2*gap/Delta_n) + 1 grows
as O(n^2), which is consistent with (and looser than) the actual |C_RC| = n.

---

**Direct Numerical Verification** (derive_step5_v2.py, exact Python Fraction arithmetic,
zero formula mismatches, zero items fixed at all n):

| n    | Z_LP       | Z_LB       | Gap    | Items fixed | |C_RC| |
|------|------------|------------|--------|-------------|--------|
| 10   | 10.820000  | 9.850000   | 0.9700 | 0           | 10     |
| 50   | 50.864800  | 49.870000  | 0.9948 | 0           | 50     |
| 200  | 200.872488 | 199.873750 | 0.9987 | 0           | 200    |
| 1000 | 1000.874500| 999.874750 | 0.9997 | 0           | 1000   |

**Formal Remark (for paper, pending review):**
Proposition 2 (Composed Counting Bound) cannot be extended to remove the Delta-spacing
hypothesis. The family (w_i = 1, v_i = 2 - i/n^2, W = floor(n/2) + 1/2) for n >= 2
has LP gap converging to 1 (bounded) while |C_RC| = n (unbounded). No function of
the LP gap alone can bound |C_RC|. The Delta > 0 hypothesis in Proposition 2 is
therefore necessary.
"""

with open('research_log/core_containment_derivation.md', encoding='utf-8') as f:
    lines = f.readlines()

# Keep lines 0..190 (1-indexed lines 1..191 = Step 4 caveats through "actual tree...")
good = lines[:191]

with open('research_log/core_containment_derivation.md', 'w', encoding='utf-8') as f:
    f.writelines(good)
    f.write(STEP5)

print("Done. Verifying...")
with open('research_log/core_containment_derivation.md', encoding='utf-8') as f:
    content = f.read()

checks = [
    ("WARNING on the hat-formula", "WARNING block"),
    ("Case A", "Case A"),
    ("Case B", "Case B"),
    ("Formal Remark", "Formal Remark"),
    ("derive_step5_v2.py", "script reference"),
    ("actual mechanism", "mechanism explanation"),
]
for phrase, label in checks:
    status = "OK" if phrase in content else "MISSING!"
    print(f"  {label}: {status}")

if "marginal loss is strictly smaller than the gap" in content:
    print("  ERROR: old invalid argument still present!")
else:
    print("  Old invalid argument removed: OK")

print(f"  Total lines: {content.count(chr(10))}")

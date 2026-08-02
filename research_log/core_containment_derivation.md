# Core Containment Derivation

## SUB-STEP 1: Marginal-Loss Formula

When an item $i < s$ (which was fully included in the LP relaxation, $x_i^{LP}=1$) is forced OUT, we lose its value $v_i$ but free up capacity $w_i$.

**a. Reallocation of freed capacity:**
Assuming the split index does not shift, the newly freed capacity $w_i$ is completely absorbed by the existing split item $s$. The fractional inclusion of $s$ increases from $R/w_s$ to $(R + w_i)/w_s$. No capacity spills over to item $s+1$ or beyond.

**b. Exact formula for $Z'_i$:**
Since the freed capacity $w_i$ is filled by item $s$, which has efficiency $e_s$, the value gained from the reallocation is $w_i e_s$. The value lost from forcing $i$ out is $v_i = w_i e_i$. 
Therefore, the new LP bound is exactly:
$$Z'_i = Z_{LP} - v_i + w_i e_s = Z_{LP} - w_i(e_i - e_s)$$
This holds as long as the capacity $w_i$ does not exceed the remaining unused capacity of item $s$.

## SUB-STEP 1.5: No-Split-Shift Condition

**a. Meaning of "split index shifts":**
The split index shifts if, after reallocating the freed capacity to item $s$, there is still capacity left over, meaning item $s$ becomes fully included ($x_s = 1$) and fractional inclusion spills over into $s+1$ (or beyond). 

**b. Algebraic derivation of the boundary:**
In the original LP, item $s$ is allocated weight $R$. Its unallocated weight is $w_s - R$.
When $w_i$ is freed, it is given to item $s$. The split index remains at $s$ if and only if the freed capacity does not exceed item $s$'s available capacity:
$$w_i \le w_s - R$$
If $w_i > w_s - R$, item $s$ is fully included, and the remaining capacity $w_i - (w_s - R)$ spills to $s+1$, causing the split index to shift to $s+1$ (or higher).

**c. Final Inequality:**
For an item $i < s$ forced OUT, the split index does not shift iff:
$$w_i \le w_s - R$$

**d. Adversarial Checks (Forcing $i < s$ OUT):**
- **Satisfies Condition:**
  Weights: `[10, 20, 30, 40, 50]`, Values: `[100, 180, 240, 280, 300]`, Capacity: `40`.
  Split is $s=2$ (weight 30), $e_s = 8$. $R = 40 - 30 = 10$.
  $Z_{LP} = 100 + 180 + 8 \times 10 = 360$.
  Test item $i=0$: $w_0 = 10$. Condition $10 \le 30 - 10$ is `True`.
  Formula: $Z'_0 = 360 - 10(10 - 8) = 340$.
  Brute-force: $Z'_0 = 340.0$. (Matches exactly).
- **Violates Condition:**
  Weights: `[25, 20, 30, 40, 50]`, Values: `[250, 180, 240, 280, 300]`, Capacity: `40`.
  Split is $s=1$ (weight 20), $e_s = 9$. $R = 40 - 25 = 15$.
  $Z_{LP} = 250 + 9 \times 15 = 385$.
  Test item $i=0$: $w_0 = 25$. Condition $25 \le 20 - 15 \implies 25 \le 5$ is `False`.
  Formula (assuming no shift): $Z'_0 = 385 - 25(10 - 9) = 360$.
  Brute-force: $Z'_0 = 340.0$. (Formula is wrong here, because capacity spilled to $s=2$).

## Symmetric Case (Forcing IN an item $j > s$)

When forcing IN an item $j > s$, it consumes capacity $w_j$. This capacity must be taken away from the fractional item $s$. 

- **Formula:** 
  Since capacity is taken from $s$ at efficiency $e_s$ and given to $j$ at efficiency $e_j$, the new LP bound is:
  $$Z'_j = Z_{LP} - w_j(e_s - e_j)$$
- **Condition for no split shift:**
  The split index does not shift as long as item $s$ has enough included weight to give up. The included weight of item $s$ is $R$.
  Therefore, the condition is:
  $$w_j \le R$$
  If $w_j > R$, we must take all of $R$ from item $s$ (removing it completely), and then take the remaining $w_j - R$ from item $s-1$, shifting the split index to $s-1$ (or lower).

**Adversarial Checks (Forcing $j > s$ IN):**
- **Satisfies Condition:**
  Weights: `[10, 20, 30, 5, 50]`, Values: `[100, 180, 240, 35, 300]`, Capacity: `40`.
  Split $s=2$ (weight 30), $R = 10$, $e_s = 8$. $Z_{LP} = 360$.
  Test item $j=3$: $w_3 = 5, e_3 = 7$. Condition $5 \le 10$ is `True`.
  Formula: $Z'_3 = 360 - 5(8 - 7) = 355$.
  Brute-force: $Z'_3 = 355.0$. (Matches exactly).
- **Violates Condition:**
  Weights: `[10, 20, 30, 40, 50]`, Values: `[100, 180, 240, 280, 300]`, Capacity: `40`.
  Split $s=2$ (weight 30), $R = 10$, $e_s = 8$. $Z_{LP} = 360$.
  Test item $j=3$: $w_3 = 40, e_3 = 7$. Condition $40 \le 10$ is `False`.
  Formula (assuming no shift): $Z'_3 = 360 - 40(8 - 7) = 320$.
  Brute-force: $Z'_3 = 280.0$. (Formula is wrong here, because capacity was stolen from $s=1$).

---

## STEP 2: Containment Theorem

### Lemma (Monotonicity of the Marginal-Loss Formula)

**Claim.** For any item $i \ne s$, the true perturbed LP bound satisfies $Z'_i \le \hat{Z}'_i$, where $\hat{Z}'_i$ is the no-split-shift formula:

$$\hat{Z}'_i = Z_{LP} - w_i |e_i - e_s|$$

That is, the formula always **overestimates** the true perturbed bound. Equality holds exactly when the no-split-shift condition is satisfied.

**Proof.**

*Case 1 ($i < s$, forced OUT):* Removing item $i$ frees capacity $w_i$. In the LP re-optimization, this freed capacity is filled greedily starting from item $s$ (the highest-efficiency unfilled item).

- If $w_i \le w_s - R$ (no split shift): all freed capacity is absorbed by item $s$ at efficiency $e_s$. The formula is exact: $Z'_i = Z_{LP} - w_i e_i + w_i e_s = \hat{Z}'_i$.

- If $w_i > w_s - R$ (split shifts): the first $(w_s - R)$ units of freed capacity are absorbed by $s$ at $e_s$, but the remaining $w_i - (w_s - R)$ units spill to item $s+1$ (or beyond) at efficiency $e_{s+1} \le e_s$ (since items are sorted by decreasing efficiency). Therefore:

$$Z'_i = Z_{LP} - w_i e_i + (w_s - R) e_s + (w_i - w_s + R) e_{s+1}$$
$$= \hat{Z}'_i + (w_i - w_s + R)(e_{s+1} - e_s) \le \hat{Z}'_i$$

since $e_{s+1} \le e_s$ and $(w_i - w_s + R) > 0$.

(If $w_i$ is large enough to also fully absorb $s+1$ and spill further, the same argument applies inductively: each successive item has even lower efficiency, so the true $Z'_i$ is even further below $\hat{Z}'_i$.)

*Case 2 ($j > s$, forced IN):* Forcing item $j$ in consumes capacity $w_j$, taken from the fractional item $s$.

- If $w_j \le R$ (no split shift): all consumed capacity comes from $s$ at efficiency $e_s$. The formula is exact: $Z'_j = Z_{LP} + w_j e_j - w_j e_s = \hat{Z}'_j$.

- If $w_j > R$ (split shifts backward): the first $R$ units are taken from $s$ at $e_s$, and the remaining $w_j - R$ units must be taken from item $s-1$ (or earlier) at efficiency $e_{s-1} \ge e_s$. The cost of lost capacity is higher than $e_s$:

$$Z'_j = Z_{LP} + w_j e_j - R \cdot e_s - (w_j - R) \cdot e_{s-1}$$
$$= \hat{Z}'_j - (w_j - R)(e_{s-1} - e_s) \le \hat{Z}'_j$$

since $e_{s-1} \ge e_s$ and $(w_j - R) > 0$.

**Verification:** Tested on 2,000 random instances (5–14 items each, 16,518 item-level checks) using exact rational arithmetic (Python `Fraction`). Zero violations of $Z'_i \le \hat{Z}'_i$ found, with 9,971 cases where the no-split-shift condition was violated.

---

### Theorem 2 (Core Containment)

**Statement.** Let $C_{RC}$ be the reduced-cost core produced by Algorithm 1 (the set of items $i$ for which $Z'_i \ge Z_{LB}$), and let $C_\delta$ be the $\delta$-band core from Definition 3 with

$$\delta^* = \frac{Z_{LP} - Z_{LB}}{w_{\min} \cdot e_s}$$

where $w_{\min} = \min_{i} w_i$. Then $C_{RC} \subseteq C_{\delta^*}$.

**Hypotheses:** Items are sorted in strictly decreasing efficiency order ($e_1 > e_2 > \cdots > e_n$), with $e_i = v_i / w_i$ and all $w_i > 0$.

**Note on the no-split-shift condition:** The no-split-shift condition from Step 1.5 is NOT required as a hypothesis. The Monotonicity Lemma above shows that the containment direction holds unconditionally — the no-split-shift condition determines whether the formula is *exact*, but containment only requires the formula to be an *upper bound*, which it always is.

**Proof.**

Let $i \in C_{RC}$, i.e., $Z'_i \ge Z_{LB}$ (item $i$ was not fixed by Algorithm 1). We must show $|e_i - e_s| \le \delta^* \cdot e_s$.

By the Monotonicity Lemma, $Z'_i \le \hat{Z}'_i = Z_{LP} - w_i |e_i - e_s|$.

Since $i \in C_{RC}$, we have $Z'_i \ge Z_{LB}$. Combined with $Z'_i \le \hat{Z}'_i$:

$$Z_{LB} \le Z'_i \le Z_{LP} - w_i |e_i - e_s|$$

Rearranging:

$$w_i |e_i - e_s| \le Z_{LP} - Z_{LB}$$

$$|e_i - e_s| \le \frac{Z_{LP} - Z_{LB}}{w_i} \le \frac{Z_{LP} - Z_{LB}}{w_{\min}} = \delta^* \cdot e_s$$

Therefore $i \in C_{\delta^*}$. $\square$

**Per-item refinement.** The proof actually shows the tighter per-item bound $|e_i - e_s| \le (Z_{LP} - Z_{LB})/w_i$. The uniform $\delta^*$ uses $w_{\min}$ to remove the item-dependence, at the cost of a possibly looser bound.

---

### Adversarial Check (Step 3)

**No-split-shift violated, containment still holds:**

Instance: $w = [10, 20, 30, 40, 50]$, $v = [100, 180, 240, 280, 300]$, $W = 40$.

Split $s = 2$ (3rd item in sorted order, $w_s = 30$, $e_s = 8$). $R = 10$.

$Z_{LP} = 360$, $Z_{LB} = 280$, gap $= 80$.

Item $j = 3$ ($e_j = 7$, $w_j = 40$): $w_j = 40 > R = 10$ — **no-split-shift is VIOLATED**.

- True $Z'_3 = 280$ (brute-force LP). Formula $\hat{Z}'_3 = 320$. Monotonicity: $280 \le 320$. ✓
- In RC-core: $280 \ge 280 = Z_{LB}$. ✓
- Delta check: $|e_3 - e_s| = 1$, gap$/w_3 = 2$. $1 \le 2$. In delta-band. ✓

**Containment holds despite the no-split-shift violation.** This is expected: the violation only makes the true $Z'$ *smaller* than the formula, so it can only cause *more* items to be fixed, never fewer.

**Exhaustive random verification:** 2,000 random instances, 16,518 item-level containment checks with exact rational arithmetic. **Zero containment failures.** (94 items landed on the exact boundary $|e_i - e_s| = (Z_{LP} - Z_{LB})/w_i$, all correctly handled by the non-strict inequality.)

---

### Step 4: Composed Counting Bound

**Proposition (Core Size Bound).** Assume in addition to the hypotheses of Theorem 2 that there exists a minimum efficiency spacing $\Delta > 0$ such that $|e_i - e_j| \ge \Delta$ for all $i \ne j$. Then:

$$|C_{RC}| \le |C_{\delta^*}| \le \left\lfloor \frac{2 \cdot \delta^* \cdot e_s}{\Delta} \right\rfloor + 1 = \left\lfloor \frac{2(Z_{LP} - Z_{LB})}{w_{\min} \cdot \Delta} \right\rfloor + 1$$

**Proof.** By Theorem 2, $|C_{RC}| \le |C_{\delta^*}|$. The $\delta$-band $C_{\delta^*}$ contains only items with $e_i \in [e_s - \delta^* e_s,\; e_s + \delta^* e_s]$, an interval of width $2 \delta^* e_s$. If the $n$ efficiencies are spaced at least $\Delta$ apart, this interval contains at most $\lfloor 2\delta^* e_s / \Delta \rfloor + 1$ items (pigeonhole). $\square$

**Consequence for $T_{LP}$.** The LP-pruned branch-and-bound tree on the core satisfies:

$$T_{LP} \le 2^{|C_{RC}|} \le 2^{\lfloor 2(Z_{LP} - Z_{LB})/(w_{\min} \Delta) \rfloor + 1}$$

Combined with Montanaro's quantum B&B (Theorem, Eq. 4), this yields a quantum query complexity of:

$$O\!\left(\sqrt{T_{LP}} \cdot m \log m \log V_{\max}\right) \le O\!\left(2^{(Z_{LP} - Z_{LB})/(w_{\min} \Delta)} \cdot m \log m \log V_{\max}\right)$$

**Important caveats:**
1. The $\Delta$-spacing assumption is a structural hypothesis, not guaranteed by the problem. For strongly correlated instances ($v_i = w_i + R/10$), efficiencies cluster near 1, making $\Delta$ small and the bound loose — consistent with the empirical observation that $\alpha \to 1$ for such instances.
2. $w_{\min}$ can be small (even 1 for integer weights), which also loosens the bound.
3. The bound $T_{LP} \le 2^m$ is a worst-case over all B&B trees with $m$ unfixed items. The actual tree is typically much smaller due to LP pruning within the core.

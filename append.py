with open('research_log/core_containment_derivation.md', 'a', encoding='utf-8') as f:
    f.write('''
---

### Step 5: Necessity of the $\Delta$-Spacing Assumption

**Proposition (Necessity of $\Delta$).** Proposition 2's dependence on $\Delta$ is necessary: no core-size bound of the form $|C_{RC}| \le f(Z_{LP} - Z_{LB})$ can hold without some density or minimum-spacing assumption on item efficiencies.

**Proof by Explicit Construction:**
Consider a parametrized family of instances indexed by $n$:
- **Items:** $n$ items, indexed $i = 1 \dots n$.
- **Weights:** $w_i = 1.0$ for all $i$.
- **Values:** $v_i = 2.0 - \frac{i}{n^2}$ for all $i$.
- **Capacity:** $W = \lfloor \frac{n}{2} \rfloor + 0.5$.

Let $s = \lfloor \frac{n}{2} \rfloor + 1$. Because $w_i = 1.0$ for all $i$, the first $s-1$ items consume $\lfloor n/2 \rfloor$ capacity. The remaining capacity is $R = 0.5$. The split item is $s$, with weight $w_s = 1.0$ and efficiency $e_s \approx 2.0$.

- **LP Bound ($Z_{LP}$):** Packs the first $s-1$ items fully, plus exactly $0.5$ of item $s$.
- **Greedy Lower Bound ($Z_{LB}$):** Packs the first $s-1$ items. The remaining capacity is $0.5$, which cannot fit any other item since all have weight $1.0$.

**Gap Analysis:**
The LP gap is exactly:
$$Z_{LP} - Z_{LB} = 0.5 \cdot v_s = 0.5 \left(2.0 - \frac{s}{n^2}\right) \approx 1.0$$
Crucially, this gap stays **bounded** (around 1.0) and does not grow with $n$.

**Reduced-Cost Core ($|C_{RC}|$):**
For any item $i$, the maximum efficiency difference from the split item is:
$$|e_i - e_s| = \left| \left(2.0 - \frac{i}{n^2}\right) - \left(2.0 - \frac{s}{n^2}\right) \right| = \frac{|i - s|}{n^2} \le \frac{n}{n^2} = \frac{1}{n}$$
Since $w_i = 1.0$, the upper bound on the marginal loss is:
$$Z_{LP} - \hat{Z}'_i = w_i |e_i - e_s| \le \frac{1}{n}$$
For $n > 1$, we have $1/n < 1.0$. Since the gap $Z_{LP} - Z_{LB} \approx 1.0$, the marginal loss is strictly smaller than the gap. Hence:
$$\hat{Z}'_i > Z_{LP} - 1.0 \approx Z_{LB}$$
Because $Z'_i \ge Z_{LB}$ for all $i = 1 \dots n$, **zero items are fixed**. The core size is $|C_{RC}| = n$.

**Conclusion:**
We have constructed a family where the LP gap is constant ($\approx 1.0$), but the core size grows linearly with $n$. Therefore, no function of the gap alone can bound the core size. The minimum-spacing parameter $\Delta$ (which in this construction shrinks as $1/n^2$) is strictly required to bound the core density.

**Direct Verification:**
The exact Algorithm 1 fixing logic (computing exact LP evaluations for each $Z'_i$) was run on this instance family for various $n$. The output confirms the analytical derivation:
- $n = 10 \quad\;\, \to \quad Z_{LP} = 10.8200 \quad Z_{LB} = 9.8500 \quad \text{Gap} = 0.9700 \quad |C_{RC}| = 10$
- $n = 50 \quad\;\, \to \quad Z_{LP} = 50.8648 \quad Z_{LB} = 49.8700 \quad \text{Gap} = 0.9948 \quad |C_{RC}| = 50$
- $n = 200 \quad \to \quad Z_{LP} = 200.8725 \;\, Z_{LB} = 199.8738 \quad \text{Gap} = 0.9987 \quad |C_{RC}| = 200$
- $n = 1000 \to \quad Z_{LP} = 1000.8745 \, Z_{LB} = 999.8747 \quad \text{Gap} = 0.9997 \quad |C_{RC}| = 1000$
''')

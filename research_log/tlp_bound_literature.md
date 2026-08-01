# T_LP Bound Literature Survey
## Step 1 — Literature Search (no derivation, no paper edits)
**Date:** 2026-08-01  
**Scope:** What is already known about analytical/theoretical bounds on LP-pruned B&B tree size for 0/1 knapsack.  
**AGENTS.md rule applied:** Read primary sources (or verified abstracts/full web content), quote exact claims, record what is NOT implied, attempt no derivation here.

---

## Search Terms Used
1. "branch and bound tree size knapsack analysis"
2. "LP relaxation knapsack tree size bound"
3. "core size bound knapsack" / "Balas Zemel 1980 core"
4. "Pisinger core problems knapsack 1999"
5. "Pisinger minimal algorithm 1997"
6. "Pisinger where are the hard knapsack problems 2005"
7. "Martello Toth 1988 knapsack branch bound"
8. "Martello Pisinger Toth 1999 combo"
9. "Kellerer Pferschy Pisinger 2004 tree size bound"
10. "Plateau Elkihel 1985 packing tree knapsack"
11. "Beier Vocking 2004 random knapsack"
12. "Kolpakov Posypkin 2010 branch bound complexity knapsack"
13. "Zemel 1984 knapsack LP bound tree"

---

## Source 1: Balas & Zemel (1980)

**Title:** An Algorithm for Large Zero-One Knapsack Problems  
**Authors:** Egon Balas, Eitan Zemel  
**Venue/Year:** Operations Research, Vol. 28, No. 5, pp. 1130-1154, 1980  
**Verified:** Title and venue confirmed via informs.org, optimization-online.org, researchgate.net.  
**Full text accessed:** NO (paywall). Claims below from verified secondary sources only.

### What it claims (from secondary sources)
Introduced the core concept: items sorted by efficiency e_i = v_i/w_i; the "core" C is the set of items with efficiencies close to the split item s. For large, uniformly distributed random instances, core size |C| is often a small fraction of n. Items outside the core can be fixed to 0 or 1 via LP reduced-cost arguments. Computational effort empirically "grew linearly with n" for random instances.

**Exact theorem statement:** UNRESOLVED. No specific O(.) theorem for |C| as f(n, gap, W_max) confirmed. The core-size observation is described as empirical/observational in all secondary sources.

**What it does NOT imply:**
- No proved closed-form upper bound on |C| for all instances.
- No formal bound on T_LP (number of B&B nodes).
- "Grows linearly in n" refers to running time, not tree size.

**Applicability to our setting:** PARTIAL. Core concept = Phase 1 of our paper. But no T_LP bound.

**Bound type:** Average-case empirical observation for random uniform instances. Not a proved theorem.

---

## Source 2: Pisinger (1999) [already cited as ref4]

**Title:** Core Problems in Knapsack Algorithms  
**Authors:** David Pisinger  
**Venue/Year:** Operations Research, Vol. 47, No. 4, pp. 570-575, 1999  
**Already cited in paper:** YES (ref4)  
**Verified:** INFORMS abstract confirmed. Full text not fetched (paywall).

### What it claims (from confirmed abstract and authoritative secondary sources)
- Exact core = minimal item set needed to guarantee optimality.
- Uniform-distribution assumption for core size is NOT realistic for hard instances.
- Predicting exact core size before solving is impossible.
- Proposes expanding core algorithms (Expknap, Minknap).
- Hardness concentrates near the split item; specific capacities create large LP gaps.

**Exact theorem statement:** UNRESOLVED for a formal O(.) bound on |C|. The quantitative contribution is empirical analysis and hardness identification, not a proved closed-form bound.

**What it does NOT imply:**
- Does NOT prove T_LP = f(n, m, gap, V_max).
- Does NOT give a tight upper bound on |C| as a function of n or the LP gap.

**Applicability to our setting:** PARTIAL. Core concept justifies alpha = m/n in our paper. No closed-form T_LP bound.

**Bound type:** Empirical/instance-class-specific. No formal theorem with explicit functional form found.

---

## Source 3: Pisinger (1997) [already cited as pisinger1997minimal]

**Title:** A Minimal Algorithm for the 0-1 Knapsack Problem  
**Authors:** David Pisinger  
**Venue/Year:** Operations Research, Vol. 45, No. 5, pp. 758-767, 1997  
**Already cited in paper:** YES  
**Verified:** informs.org, diku.dk author page.

### What it claims
Minknap = expanding-core DP/B&B that enumerates the symmetrically smallest core sufficient for optimality. Provably terminates with the minimal core.

**Exact theorem statement:** UNRESOLVED for O(.) bound on |C| or T_LP. The core size is not bounded analytically beyond trivial worst-case |C| = n.

**Applicability to our setting:** LOW for T_LP bounding. Already cited.

**Bound type:** Algorithm correctness proof. No explicit tree-size or core-size bound with functional form.

---

## Source 4: Pisinger (2005)

**Title:** Where Are the Hard Knapsack Problems?  
**Authors:** David Pisinger  
**Venue/Year:** Computers & Operations Research, Vol. 32, No. 9, pp. 2271-2284, 2005  
**Not currently cited in paper.**  
**Verified:** gla.ac.uk preprint, researchgate.net.

### What it claims
- New hard benchmark classes designed to defeat LP-based pruning.
- B&B tree size is instance-structure-dependent: identical efficiencies defeat LP pruning (large T_LP); well-separated efficiencies enable tight pruning (small T_LP).
- LP gap is the primary driver of difficulty.

**Exact theorem statement:** No formal theorem bounding T_LP as f(instance parameters) found.

**What it does NOT imply:** No closed-form bound on T_LP or |C|.

**Applicability to our setting:** MEDIUM for motivation/justification. Confirms our empirical observation that subset-sum/strongly-correlated -> large T_LP. Cannot provide an analytical bound.

**Bound type:** Empirical/experimental hardness characterization.

---

## Source 5: Martello, Pisinger & Toth (1999) [already cited as martello1999combo]

**Title:** Dynamic Programming and Strong Bounds for the 0-1 Knapsack Problem  
**Authors:** Silvano Martello, David Pisinger, Paolo Toth  
**Venue/Year:** Management Science, Vol. 45, No. 3, pp. 414-424, 1999  
**Already cited in paper:** YES  
**Verified:** informs.org, repec.org.

### What it claims
Combo algorithm = LP/surrogate relaxation + valid inequalities + DP for the core. Solved 10,000-item instances in <0.2 seconds empirically.

**Exact theorem statement:** No secondary source reports a proved theorem bounding B&B node counts as f(instance parameters).

**Applicability to our setting:** LOW for T_LP bounding. Already cited.

**Bound type:** Empirical performance. No explicit tree-size theorem.

---

## Source 6: Martello & Toth (1988) [already cited as martello1988mtm]

**Title:** A New Algorithm for the 0-1 Knapsack Problem  
**Authors:** Silvano Martello, Paolo Toth  
**Venue/Year:** Management Science, Vol. 34, No. 5, pp. 633-644, 1988  
**Already cited in paper:** YES  
**Verified:** Multiple sources.

### What it claims
MT algorithm: LP relaxation upper bound + variable fixing + backtracking. Martello-Toth bound is tighter than raw Dantzig. Empirically polynomial average time.

**Exact theorem statement:** No proved O(.) bound on T_LP found.

**Applicability to our setting:** LOW for T_LP bounding. Already cited.

**Bound type:** Empirical. No explicit tree-size theorem.

---

## Source 7: Plateau & Elkihel (1985) [already cited as ref7]

**Title:** Analysis and Optimisation of the Packing Tree Search Algorithm for the Knapsack Problem  
**Authors:** G. Plateau, M. Elkihel  
**Venue/Year:** European Journal of Operational Research, Vol. 19, No. 2, pp. 211-222, 1985  
**Already cited in paper:** YES (ref7)  
**Full text accessed:** NO. Title from references.bib.

### What it claims (from secondary sources)
- Analyzes the "packing tree" (B&B tree) search for knapsack with LP-based bounding.
- The title directly says "Analysis and Optimisation of the Packing Tree Search Algorithm" -- this is the most promising title in our search for a tree-size analysis theorem.
- Secondary sources describe contributions as pruning analysis and performance characterization, but do not quote a specific O(.) theorem.

**Exact theorem statement:** UNRESOLVED. Cannot confirm or rule out without full text.

**Applicability to our setting:** UNRESOLVED -- title is most promising. NEEDS PRIMARY SOURCE ACCESS.

**Status:** HIGHEST PRIORITY for primary text retrieval before Step 2. The title "analysis and optimisation of packing tree search" suggests this paper might be exactly the tree-size analysis we need.

**Bound type:** UNRESOLVED.

---

## Source 8: Beier & Vocking (2004) [already cited as beier2004random]

**Title:** Random Knapsack in Expected Polynomial Time  
**Authors:** Rene Beier, Berthold Vocking  
**Venue/Year:** Journal of Computer and System Sciences, Vol. 69, No. 3, pp. 306-329, 2004 (STOC 2003 conference version)  
**Already cited in paper:** YES (beier2004random)  
**Verified:** Multiple sources confirm title/venue/year.

### What it claims (confirmed from multiple authoritative secondary sources)
**Central theorem (informal):** For instances where profits are drawn i.i.d. from a "wide class of distributions" (weights can be adversarial), the expected number of Pareto-optimal solutions (dominating solutions) is polynomially bounded in n -- specifically O(n^k) for a small constant k (secondary sources cite O(n^3) to O(n^4) depending on distribution assumptions). This implies the Nemhauser-Ullmann DP runs in expected polynomial time.

For smoothed analysis (inputs perturbed by Gaussian/uniform noise with std sigma), the bound is O(n^k / sigma). Holds even when weights are fixed adversarially.

**What it does NOT imply:**
- This bounds Pareto-optimal DP states, NOT the size of an LP-pruned B&B tree.
- The DP is Nemhauser-Ullmann (enumeration of dominating profit-weight pairs), different from Dantzig-bound B&B.
- Bound is average-case / smoothed-analysis -- does NOT apply to all instances.
- Does NOT bound T_LP for worst-case or structured instances (subset-sum, strongly correlated) -- exactly our hard regime.

**Adaptation required:** Significant. Would need: (1) showing T_LP is bounded by number of Pareto-optimal DP states; (2) restriction to random-profit instances; (3) reconciling that subset-sum / strongly-correlated are exactly the hard cases where this bound fails.

**Applicability to our setting:** LOW-MEDIUM. Offers a smoothed-analysis paradigm that could inspire a similar T_LP analysis, but is NOT directly applicable to LP-pruned B&B in our setting.

**Bound type:** Average-case / smoothed analysis for random profit distributions.

---

## Source 9: Kolpakov & Posypkin (2010)

**Title:** Upper and Lower Bounds for the Complexity of the Branch and Bound Method for the Knapsack Problem  
**Authors:** R. M. Kolpakov, M. A. Posypkin  
**Venue/Year:** Discrete Mathematics and Applications, Vol. 20, No. 1, pp. 95-112, 2010  
**DOI:** 10.1515/DMA.2010.006  
**Not currently cited in paper.**  
**Full text accessed:** NO. Confirmed from researchgate.net abstract, mathnet.ru.

### What it claims (from secondary sources)
- Establishes TWO EXPLICIT UPPER BOUNDS on the number of steps (nodes) of a specific B&B algorithm for the 1D Boolean knapsack problem.
- Identifies a subclass of knapsack instances where B&B complexity is polynomially bounded in n.
- Proves upper AND lower bounds on B&B complexity for the subset sum problem specifically.
- The B&B variant analyzed: branching along the variable with maximal weight.
- "Complexity" = number of nodes in the search tree.

**Exact theorem statement:** UNRESOLVED at this level of access. Secondary sources confirm the existence of formal upper bounds and a polynomial-complexity subclass but do not quote the explicit functional forms.

**What it does NOT imply (from secondary sources):**
- Unclear whether the bounding oracle is LP relaxation or simpler feasibility bounding.
- "Polynomial-complexity subclass" definition needs verification -- may not match our LP-pruned setting.
- Whether the subset-sum bounds transfer to general knapsack is unclear.

**Applicability to our setting:** MEDIUM -- closest paper found to an explicit formal T_LP-type theorem. But the LP-oracle question is critical. NEEDS PRIMARY SOURCE ACCESS.

**Status:** SECOND PRIORITY for primary text retrieval. This is the only paper found that explicitly claims to prove formal upper and lower bounds on B&B node counts for knapsack.

**Bound type:** Worst-case analytical bounds on node count, for specific B&B variants.

---

## Source 10: Kellerer, Pferschy & Pisinger (2004) [already cited as ref3]

**Title:** Knapsack Problems  
**Authors:** Hans Kellerer, Ulrich Pferschy, David Pisinger  
**Venue/Year:** Springer, Berlin, 2004 (monograph)  
**Already cited in paper:** YES (ref3)  
**Verified:** Standard reference, multiple secondary sources.

### What it claims (from secondary sources on book content)
- Chapter 5 covers exact B&B for 0-1 KP. Section 5.1.1: LP-based upper bounds and how tightness determines tree size.
- The book discusses: (1) tight LP bounds -> small trees; (2) loose bounds (strongly correlated) -> large trees; (3) core-problem approach concentrates difficulty in |C| items.
- No single "tree size theorem" with O(.) form reported in any secondary source.

**Exact theorem statement:** UNRESOLVED. No specific theorem number/statement with O(.) form found through secondary sources.

**Applicability to our setting:** MEDIUM as comprehensive citation. Chapter 5 should be consulted for any formal theorem about tree-size/LP-bound interaction.

**Status:** Requires book access to confirm or rule out a formal theorem.

**Bound type:** UNKNOWN from secondary sources; likely descriptive/empirical rather than formal theorem.

---

## Summary Table

| Source | Formal T_LP Bound? | Bound Type | Directly Applicable? | Priority |
|--------|-------------------|------------|----------------------|----------|
| Balas & Zemel 1980 | NO (empirical) | Avg-case, random | PARTIAL (core concept) | Low -- already absorbed |
| Pisinger 1999 (ref4) | NO (empirical) | Instance-class | PARTIAL | Low -- already cited |
| Pisinger 1997 | NO (algorithm correctness) | Algorithm | Low | Low -- already cited |
| Pisinger 2005 | NO (empirical taxonomy) | Instance-class | Medium (justify experiments) | Low-Medium |
| Martello+Pisinger+Toth 1999 | NO (empirical speed) | Empirical | Low | Low -- already cited |
| Martello & Toth 1988 | NO (empirical speed) | Empirical | Low | Low -- already cited |
| Plateau & Elkihel 1985 (ref7) | UNRESOLVED | UNKNOWN | UNRESOLVED | HIGH -- get full text |
| Beier & Vocking 2004 | PARTIAL (DP states, not B&B) | Smoothed analysis | Low-Medium | Medium -- adapt paradigm |
| Kolpakov & Posypkin 2010 | POSSIBLY YES | Worst-case analytical | Medium (LP oracle unclear) | HIGH -- get full text |
| Kellerer et al. 2004 (ref3) | UNKNOWN | Unknown | Medium | Medium -- check book |

---

## Key Finding

NO directly applicable, closed-form, analytical bound on T_LP as a function of instance parameters (n, W_max, V_max, LP integrality gap, core size) was found in any verified source.

The literature treats T_LP as:
- Instance-dependent and hard to predict analytically in the worst case.
- Empirically small for random uniform instances (Balas-Zemel, Pisinger 1997/1999).
- Empirically large for strongly correlated/subset-sum instances (Pisinger 2005).
- Bounded in expected polynomial time for Pareto-optimal DP states under random profits (Beier-Vocking 2004) -- but that bounds a different quantity.
- POSSIBLY bounded by formal worst-case analysis in Kolpakov-Posypkin 2010 (unverified).

Closest existing result: Kolpakov & Posypkin (2010) -- explicit upper/lower bounds on B&B nodes for knapsack. Whether LP relaxation is the bounding oracle (matching our setting) is UNRESOLVED.

Plateau & Elkihel (1985) (ref7) -- title "analysis and optimisation of packing tree search" most directly suggests tree-size analysis for LP-pruned knapsack B&B. Full theorem content UNVERIFIED.

---

## Recommendation for Step 2

**Track A -- Obtain primary texts (mandatory before Step 2 derivation):**
1. GET: Plateau & Elkihel (1985, EJOR 19(2):211-222) -- confirm or rule out tree-size theorem.
2. GET: Kolpakov & Posypkin (2010, Discrete Math. Appl. 20(1):95-112) -- check if LP is the bounding oracle and quote exact theorems.

**Track B -- Assess adaptation or original derivation:**
- If Plateau-Elkihel or Kolpakov-Posypkin contain applicable theorems: assess adaptation to our setting (LP Dantzig bound, reduced-cost pre-fixing, depth d = m), then attempt adaptation (Step 2a).
- If neither is applicable: proceed to Step 2b = original, narrower bound from scratch. Natural starting points would include:
  * Trivial upper bound: T_LP <= 2^m (too weak but formally correct).
  * LP integrality gap bound: items with |reduced_cost| > Delta are fixed, so |C| is bounded by the number of items within efficiency band [e_s - epsilon, e_s + epsilon] where epsilon = Delta / (w_s * e_s). Derivation deferred to Step 2.
  * Smoothed-analysis paradigm (Beier-Vocking template): average-case T_LP bound under random profit perturbations.
  * NOTE: These are directions, not claims. No derivation in this log.

**Step 2 assessment:** "Adapt an existing result" requires primary source access first. If those sources fail, Step 2 must be "attempt an original, narrower bound from scratch."

---

*Log created 2026-08-01. No derivations attempted. No paper edits made. All claims classified per MEASURED/DERIVED/UNRESOLVED taxonomy.*

"""
Figures for the MEASURED quantum-walk results (quantum_walk_results.json).

Produces two PDFs in paper/figures/:
  1. quantum_walk_scaling.pdf  -- measured decisive quantum queries vs sqrt(T*m),
     pooled across classes, with a through-origin linear fit (confirms
     Q = Theta(sqrt(T*m)) empirically).
  2. quantum_walk_crossover.pdf -- for the LP-hard classes (subset-sum, strongly
     correlated), measured quantum queries vs classical B&B nodes and MitM as a
     function of n, showing the crossover where quantum wins.
"""

import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

with open(os.path.join(HERE, "quantum_walk_results.json")) as f:
    res = json.load(f)
rows = res["data"]

CLASS_COLORS = {
    "uncorrelated": "#1f77b4",
    "weakly_correlated": "#ff7f0e",
    "strongly_correlated": "#d62728",
    "subset_sum": "#2ca02c",
    "inverse_strongly": "#9467bd",
}
LABELS = {
    "uncorrelated": "Uncorrelated",
    "weakly_correlated": "Weakly corr.",
    "strongly_correlated": "Strongly corr.",
    "subset_sum": "Subset-sum",
    "inverse_strongly": "Inv. strongly",
}


def fig_scaling():
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    xs_all, ys_all = [], []
    for cls, color in CLASS_COLORS.items():
        td = [r for r in rows if r["type"] == cls]
        if not td:
            continue
        x = np.array([r["sqrt_Tm"] for r in td])
        y = np.array([r["montanaro_queries_decisive"] for r in td])
        ax.scatter(x, y, s=18, color=color, alpha=0.7, label=LABELS[cls])
        xs_all.extend(x.tolist())
        ys_all.extend(y.tolist())
    xs_all = np.array(xs_all)
    ys_all = np.array(ys_all)
    # through-origin least squares slope
    slope = float(np.dot(xs_all, ys_all) / np.dot(xs_all, xs_all))
    xfit = np.linspace(0, xs_all.max() * 1.05, 50)
    ax.plot(xfit, slope * xfit, "k--", lw=1.3,
            label=fr"fit: $Q \approx {slope:.2f}\,\sqrt{{T_{{\rm LP}}\,m}}$")
    ax.set_xlabel(r"$\sqrt{T_{\rm LP}\, m}$ (Montanaro prediction)")
    ax.set_ylabel("measured quantum queries $Q$")
    ax.set_title("Measured quantum query count vs. Montanaro bound")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "quantum_walk_scaling.pdf")
    fig.savefig(out)
    print("wrote", out, f"(through-origin slope={slope:.3f})")


def fig_crossover():
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    for cls in ("subset_sum", "strongly_correlated"):
        td = [r for r in rows if r["type"] == cls]
        if not td:
            continue
        ns = sorted(set(r["n"] for r in td))
        c_mean = [np.mean([r["classical_nodes"] for r in td if r["n"] == n]) for n in ns]
        c_std = [np.std([r["classical_nodes"] for r in td if r["n"] == n]) for n in ns]
        q_mean = [np.mean([r["montanaro_queries_decisive"] for r in td if r["n"] == n]) for n in ns]
        q_std = [np.std([r["montanaro_queries_decisive"] for r in td if r["n"] == n]) for n in ns]
        color = CLASS_COLORS[cls]
        ax.errorbar(ns, c_mean, yerr=c_std, fmt="-o", color=color, lw=1.5, ms=4,
                    capsize=2, label=f"{LABELS[cls]}: classical B&B nodes")
        ax.errorbar(ns, q_mean, yerr=q_std, fmt="--s", color=color, lw=1.5, ms=4,
                    capsize=2, alpha=0.8, label=f"{LABELS[cls]}: quantum queries")
    ns_mitm = sorted(set(r["n"] for r in rows))
    ax.plot(ns_mitm, [2 ** (n // 2) for n in ns_mitm], ":k", lw=1.2,
            label=r"MitM $2^{n/2}$")
    ax.set_yscale("log")
    ax.set_xlabel("number of items $n$")
    ax.set_ylabel("operations (log scale)")
    ax.set_title("Measured quantum vs. classical on LP-hard instances")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "quantum_walk_crossover.pdf")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    fig_scaling()
    fig_crossover()

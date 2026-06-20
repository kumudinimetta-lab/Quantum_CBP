"""Break-even figure from resource_estimate.json."""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(FIG, exist_ok=True)

d = json.load(open(os.path.join(HERE, "resource_estimate.json")))
proj = d["breakeven_projection"]
ms = [p["m"] for p in proj]
cl = [p["classical_ops"] for p in proj]
qt = [p["quantum_T_total"] for p in proj]
mstar = d["breakeven_core_size"]

fig, ax = plt.subplots(figsize=(5.0, 3.6))
ax.plot(ms, cl, "-o", color="#d62728", lw=1.6, ms=4,
        label=r"classical B&B work $\sim T_{\rm LP}\,m$")
ax.plot(ms, qt, "--s", color="#1f77b4", lw=1.6, ms=4,
        label=r"quantum fault-tolerant $T$-count")
if mstar:
    ax.axvline(mstar, color="k", ls=":", lw=1.2)
    ax.text(mstar + 1, ax.get_ylim()[0] * 1, f"  break-even $m^*\\approx{mstar}$",
            rotation=90, va="bottom", fontsize=8)
ax.set_yscale("log")
ax.set_xlabel("core size $m$ (LP-hard regime)")
ax.set_ylabel("operations / $T$-gates (log scale)")
ax.set_title("Fault-tolerant break-even: quantum vs. classical")
ax.legend(fontsize=7.5, loc="upper left")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
out = os.path.join(FIG, "resource_breakeven.pdf")
fig.savefig(out)
print("wrote", out)

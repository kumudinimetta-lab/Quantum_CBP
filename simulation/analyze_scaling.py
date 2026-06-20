"""
Statistical analysis of the measured quantum query scaling.
Reads quantum_walk_results.json (per-seed measured data) and reports, with
95% confidence intervals:
  (1) log-log power-law exponent  Q_d ~ (T_LP*m)^beta   (expect beta ~ 0.5),
  (2) through-origin constant c in Q_d ~ c*sqrt(T_LP*m),
  (3) pooled ratio Q_d / sqrt(T_LP*m).
Also writes scaling_stats.json for downstream use in the paper.
"""

import json
import numpy as np
from scipy import stats


def main():
    with open("quantum_walk_results.json") as f:
        blob = json.load(f)
    rows = blob["data"]

    qd = np.array([r["montanaro_queries_decisive"] for r in rows], dtype=float)
    tlp = np.array([r["T_LP"] for r in rows], dtype=float)
    m = np.array([r["depth"] for r in rows], dtype=float)
    s = np.sqrt(tlp * m)
    n = len(rows)

    # (1) log-log power-law fit: log Qd = log c + beta * log(T_LP*m)
    x = np.log(tlp * m)
    y = np.log(qd)
    lr = stats.linregress(x, y)
    beta = lr.slope
    # 95% CI on slope via t-distribution
    tcrit = stats.t.ppf(0.975, df=n - 2)
    beta_lo, beta_hi = beta - tcrit * lr.stderr, beta + tcrit * lr.stderr
    r2 = lr.rvalue ** 2

    # (2) through-origin fit Qd = c * s : c_hat = sum(s*qd)/sum(s^2)
    c_hat = float(np.sum(s * qd) / np.sum(s * s))
    resid = qd - c_hat * s
    # variance of c_hat for no-intercept model
    sigma2 = np.sum(resid ** 2) / (n - 1)
    var_c = sigma2 / np.sum(s * s)
    se_c = np.sqrt(var_c)
    c_lo, c_hi = c_hat - tcrit * se_c, c_hat + tcrit * se_c
    # R^2 for through-origin model (uncentered)
    ss_res = np.sum(resid ** 2)
    ss_tot_unc = np.sum(qd ** 2)
    r2_origin = 1 - ss_res / ss_tot_unc

    # (3) pooled ratio
    ratio = qd / s
    rmean = float(np.mean(ratio))
    rsd = float(np.std(ratio, ddof=1))
    rse = rsd / np.sqrt(n)
    r_lo, r_hi = rmean - tcrit * rse, rmean + tcrit * rse

    print(f"N data points (per-seed): {n}")
    print("-" * 60)
    print(f"(1) Power-law exponent beta: {beta:.3f}  "
          f"95% CI [{beta_lo:.3f}, {beta_hi:.3f}]   R^2={r2:.3f}")
    print(f"(2) Through-origin c (Qd=c*sqrt(T*m)): {c_hat:.3f}  "
          f"95% CI [{c_lo:.3f}, {c_hi:.3f}]   R^2(origin)={r2_origin:.3f}")
    print(f"(3) Pooled ratio Qd/sqrt(T*m): mean={rmean:.3f}  "
          f"95% CI [{r_lo:.3f}, {r_hi:.3f}]  sd={rsd:.3f}")

    out = {
        "n_points": n,
        "exponent_beta": beta,
        "exponent_ci95": [beta_lo, beta_hi],
        "exponent_r2": r2,
        "origin_c": c_hat,
        "origin_c_ci95": [c_lo, c_hi],
        "origin_r2": r2_origin,
        "ratio_mean": rmean,
        "ratio_ci95": [r_lo, r_hi],
        "ratio_sd": rsd,
    }
    with open("scaling_stats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved -> scaling_stats.json")


if __name__ == "__main__":
    main()

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
import os

# --- Generators from benchmark_v5.py ---
def gen_uncorrelated(n, seed=None, R=100, cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R+1, size=n).tolist()
    v = rng.randint(1, R+1, size=n).tolist()
    cap = int(cap_ratio * sum(w))
    return w, v, cap

def gen_weakly_correlated(n, seed=None, R=100, cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R+1, size=n).tolist()
    v = [max(1, wi + rng.randint(-R//10, R//10 + 1)) for wi in w]
    cap = int(cap_ratio * sum(w))
    return w, v, cap

def gen_strongly_correlated(n, seed=None, R=100, cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R+1, size=n).tolist()
    v = [wi + R // 10 for wi in w]
    cap = int(cap_ratio * sum(w))
    return w, v, cap

def gen_subset_sum(n, seed=None, R=100, cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    w = rng.randint(1, R+1, size=n).tolist()
    v = list(w)
    cap = int(cap_ratio * sum(w))
    return w, v, cap

def gen_inverse_strongly(n, seed=None, R=100, cap_ratio=0.5):
    rng = np.random.RandomState(seed)
    v = rng.randint(1, R+1, size=n).tolist()
    w = [vi + R // 10 for vi in v]
    cap = int(cap_ratio * sum(w))
    return w, v, cap

def lp_bound(weights, values, capacity):
    items = list(range(len(weights)))
    items_sorted = sorted(items, key=lambda i: values[i]/max(weights[i], 1e-10), reverse=True)
    remaining = capacity
    total = 0.0
    for i in items_sorted:
        if remaining <= 0:
            break
        if weights[i] <= remaining:
            remaining -= weights[i]
            total += values[i]
        else:
            total += (values[i] / max(weights[i], 1e-10)) * remaining
            remaining = 0
    return total

def brute_force(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            if dp[c - w] + v > dp[c]:
                dp[c] = dp[c - w] + v
    return dp[capacity]

gen_map = {
    'uncorrelated': gen_uncorrelated,
    'weakly_correlated': gen_weakly_correlated,
    'strongly_correlated': gen_strongly_correlated,
    'subset_sum': gen_subset_sum,
    'inverse_strongly': gen_inverse_strongly
}

print('Loading dataset...')
with open('../benchmark_results_v5_hard.json', 'r') as f:
    d = json.load(f)['data']

rows = []
trial_counter = 0
prev_n = None
prev_type = None

for r in d:
    if r['n'] != prev_n or r['type'] != prev_type:
        trial_counter = 0
    
    seed = r['n'] * 1000 + trial_counter
    gen_func = gen_map[r['type']]
    w, v, cap = gen_func(r['n'], seed=seed)
    
    z_lp = lp_bound(w, v, cap)
    z_star = brute_force(w, v, cap)
    gap = z_lp - z_star
    
    rows.append({
        'n': r['n'],
        'm': r['m'],
        'T_full': r['T_full'],
        'type': r['type'],
        'gap': gap,
        'seed': seed
    })
    
    prev_n = r['n']
    prev_type = r['type']
    trial_counter += 1

df = pd.DataFrame(rows)

output = []
def log(s):
    print(s)
    output.append(s)

log('--- DATA SOURCING ---')
log(f'Loaded {len(df)} instances.')
zero_gap = (df['gap'] == 0).sum()
zero_T = (df['T_full'] == 0).sum()
log(f'Instances with gap=0: {zero_gap}')
log(f'Instances with T_full=0: {zero_T}')
log('Handling zero gaps: adding epsilon=1e-6 to gap for log transform.')

df['log_gap'] = np.log(df['gap'] + 1e-6)
df['log_T'] = np.log(df['T_full'])

log('\n--- CORRELATION MATRIX ---')
log(df[['m', 'gap', 'n', 'log_T']].corr().to_string())

def fit_and_report(data, name, formula):
    log(f'\n=============================================')
    log(f'MODEL: {name}')
    log(f'Formula: {formula}')
    log(f'N = {len(data)}')
    
    if len(data) < 10:
        log('Not enough data to fit.')
        return
        
    model = smf.ols(formula, data=data).fit()
    log(model.summary().as_text())
    
    # K-Fold CV
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2 = []
    for train_idx, test_idx in kf.split(data):
        train = data.iloc[train_idx]
        test = data.iloc[test_idx]
        m_cv = smf.ols(formula, data=train).fit()
        preds = m_cv.predict(test)
        
        target = formula.split('~')[0].strip()
        y_true = test[target]
        cv_r2.append(r2_score(y_true, preds))
        
    log(f'5-Fold CV Out-of-Sample R2: {np.mean(cv_r2):.4f} (std: {np.std(cv_r2):.4f})')

# Pooled Model
fit_and_report(df, 'POOLED ALL CLASSES', 'log_T ~ log_gap + m')

# Adding n
fit_and_report(df, 'POOLED ALL CLASSES (with n)', 'log_T ~ log_gap + m + n')

# Interaction model
fit_and_report(df, 'POOLED ALL CLASSES (interaction)', 'log_T ~ log_gap * m')

# Per-class models
for t in df['type'].unique():
    fit_and_report(df[df['type'] == t], f'PER-CLASS: {t}', 'log_T ~ log_gap + m')

with open('raw_results/regression_output.txt', 'w') as f:
    f.write('\n'.join(output))

print('Done.')

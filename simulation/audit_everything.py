import json, numpy as np
from scipy import stats

def ci_binomial(k, n, conf=0.95):
    import scipy.stats as stats
    if n == 0: return (0,0)
    low = stats.beta.ppf((1-conf)/2, k, n-k+1) if k > 0 else 0
    high = stats.beta.ppf(1-(1-conf)/2, k+1, n-k) if k < n else 1
    return low, high

print('=== STATISTICAL AUDIT ===')
try:
    with open('quantum_walk_spectral_full.json') as f:
        data = json.load(f)
    records = data.get('records', [])
    marked, unmarked = [], []
    for r in records:
        if r.get('status') == 'COMPLETED':
            p = r.get('p_accepts', {}).get('s0')
            if p is not None:
                if r.get('case_type') == 'marked': marked.append(p)
                elif r.get('case_type') == 'unmarked': unmarked.append(p)
    marked, unmarked = np.array(marked), np.array(unmarked)
    print(f'Marked N: {len(marked)}')
    print(f'Unmarked N: {len(unmarked)}')
    if len(marked)>0 and len(unmarked)>0:
        print(f'Median Marked: {np.median(marked)}')
        print(f'Median Unmarked: {np.median(unmarked)}')
        u, p = stats.mannwhitneyu(marked, unmarked, alternative='greater')
        print(f'U: {u}, p: {p}')
        print(f'CI 400/400: {ci_binomial(400,400)}')
        print(f'CI 489/489: {ci_binomial(489,489)}')
        print(f'CI 889/889: {ci_binomial(889,889)}')
except Exception as e:
    print('Error:', e)

print('\n=== LARGE SCALE ALPHA AUDIT ===')
try:
    with open('large_scale_benchmark.json') as f:
        data = json.load(f)
    for n_str, classes in data.items():
        for cls_name, c_data in classes.items():
            if 'alphas' in c_data:
                alphas = np.array(c_data['alphas'])
                print(f'{cls_name} | {n_str} | {len(alphas)} | {np.median(alphas):.5f} | {np.percentile(alphas,75)-np.percentile(alphas,25):.5f} | {np.mean(alphas):.5f} | {np.std(alphas):.5f} | {np.min(alphas):.5f} | {np.max(alphas):.5f}')
except Exception as e:
    print('Error:', e)

print('\n=== RUNTIME AUDIT ===')
try:
    with open('runtime_memory_raw.json') as f:
        data = json.load(f)
    print(f'Total runtime records: {len(data)}')
    methods = set(r.get('method') for r in data if 'method' in r)
    ns = set(r.get('n') for r in data if 'n' in r)
    print(f'Methods: {methods}')
    print(f'Ns: {ns}')
except Exception as e:
    print('Error:', e)

print('\n=== HARDWARE AUDIT ===')
try:
    with open('ibm_hardware_results.json') as f:
        data = json.load(f)
    print(f'Hardware keys: {list(data.keys())}')
    if 'instances' in data:
        print(f'First instance keys: {list(data["instances"][0].keys())}')
except Exception as e:
    print('Error:', e)

print('\n=== ORACLE AUDIT ===')
try:
    with open('oracle_gate_counts.json') as f:
        d = json.load(f)
        print(d.get('note'))
    with open('resource_estimate.json') as f:
        d = json.load(f)
        print(d.get('note'))
        print(d['per_oracle_profiles'][0])
except Exception as e:
    print('Error:', e)

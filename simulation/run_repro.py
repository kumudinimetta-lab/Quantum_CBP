import json
from benchmark_v5 import gen_uncorrelated, reduced_cost_fixing

n = 12
# We know from quantum_walk_results.json the seeds are 1000*n + t. Let's use t=0.
seed = 1000 * 12 + 0
w, v, cap, _ = gen_uncorrelated(n, seed)
fi, core, fo = reduced_cost_fixing(n, w, v, cap)

m = len(core)
number_fixed = len(fi) + len(fo)
max_nodes = 2**(m+1) - 1

# From quantum_walk_results.json, let's find the uncorrelated n=12 run
with open('quantum_walk_results.json', 'r') as f:
    qw = json.load(f)['data']

recorded_run = None
for r in qw:
    if r['type'] == 'uncorrelated' and r['n'] == 12:
        recorded_run = r
        break

print(f'Original n: {n}')
print(f'Number fixed: {number_fixed}')
print(f'Resulting core size (m): {m}')
print(f'Theoretical max nodes (2^(m+1)-1): {max_nodes}')
if recorded_run:
    print(f"Recorded tree nodes (T_LP): {recorded_run['T_LP']}")
    print(f"Recorded depth: {recorded_run['depth']}")
    print(f"Quantum query count: {recorded_run['montanaro_queries_decisive']}")

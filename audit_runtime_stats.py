import json
import numpy as np
from scipy import stats

def compute_runtime_stats():
    with open('simulation/runtime_memory_raw.json') as f:
        data = json.load(f)
        
    print("=== RUNTIME AND MEMORY CHARACTERIZATION ===")
    print(f"Total Records: {len(data)}")
    
    # Store by (method, class, n)
    # Each record represents a seed and has a list of runtimes and peak_mems
    metrics = {}
    
    for r in data:
        method = r.get('method')
        if not method: continue
        
        c = r['class']
        n = r['n']
        
        key = (method, c, n)
        if key not in metrics:
            metrics[key] = {'runtimes_ns': [], 'peak_mem_bytes': []}
            
        # Extract median across repetitions for this specific instance
        rt = r.get('runtimes_ns')
        if rt and len(rt) > 0:
            metrics[key]['runtimes_ns'].append(np.median(rt))
            
        pm = r.get('peak_mem_bytes')
        if pm and len(pm) > 0:
            metrics[key]['peak_mem_bytes'].append(np.median(pm))
            
    # Print summary stats
    methods = ["Classical B&B", "LP-pruned B&B", "Hybrid quantum simulation"]
    ns = [12, 14, 16, 18, 20]
    classes = ["Uncorrelated", "Weakly correlated", "Strongly correlated", "Subset-sum", "Inverse strongly"]
    
    for method in methods:
        print(f"\n--- Method: {method} ---")
        for c in classes:
            for n in ns:
                key = (method, c, n)
                if key in metrics:
                    rts = np.array(metrics[key]['runtimes_ns']) / 1e6 # ms
                    mems = np.array(metrics[key]['peak_mem_bytes']) / 1024 # KB
                    
                    if len(rts) > 0:
                        print(f"{c:25} | n={n:2} | N={len(rts):2} | Time: med={np.median(rts):.2f}ms, IQR={np.percentile(rts,75)-np.percentile(rts,25):.2f}ms, mean={np.mean(rts):.2f}ms, sd={np.std(rts):.2f}ms | Mem: med={np.median(mems):.1f}KB, IQR={np.percentile(mems,75)-np.percentile(mems,25):.1f}KB, mean={np.mean(mems):.1f}KB, sd={np.std(mems):.1f}KB")
                        
    # Paired Analysis
    print("\n=== PAIRED CLASSICAL VS LP-PRUNED ANALYSIS ===")
    
    for c in classes:
        for n in ns:
            class_pairs_time = []
            
            # Find seeds for this class/n
            seeds = set()
            for r in data:
                if r['class'] == c and r['n'] == n:
                    seeds.add(r['seed'])
                    
            valid_pairs = 0
            for seed in sorted(seeds):
                # find classical
                c_rt = None
                lp_rt = None
                for r in data:
                    if r['class'] == c and r['n'] == n and r['seed'] == seed:
                        if r['method'] == 'Classical B&B':
                            rt = r.get('runtimes_ns')
                            if rt: c_rt = np.median(rt) / 1e6
                        elif r['method'] == 'LP-pruned B&B':
                            rt = r.get('runtimes_ns')
                            if rt: lp_rt = np.median(rt) / 1e6
                
                if c_rt is not None and lp_rt is not None:
                    class_pairs_time.append((c_rt, lp_rt))
                    valid_pairs += 1
            
            if len(class_pairs_time) > 0:
                c_arr = np.array([x[0] for x in class_pairs_time])
                lp_arr = np.array([x[1] for x in class_pairs_time])
                diffs = c_arr - lp_arr
                
                print(f"{c:25} | n={n:2} | N_pairs={valid_pairs:2} | C_med={np.median(c_arr):.2f}ms | LP_med={np.median(lp_arr):.2f}ms | Ratio(C/LP)={np.median(c_arr)/np.median(lp_arr):.2f}")
                
                # Exclude exactly zero differences for wilcoxon
                non_zero = diffs[diffs != 0]
                if len(non_zero) > 0:
                    stat, p = stats.wilcoxon(c_arr, lp_arr, zero_method='wilcox')
                    print(f"  Wilcoxon signed-rank: W={stat}, p={p:.5e}")
                else:
                    print("  Wilcoxon signed-rank: SKIPPED (all differences exactly zero)")

if __name__ == '__main__':
    compute_runtime_stats()

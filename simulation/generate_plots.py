import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def generate_publication_plots(json_file='benchmark_results_v5_hard.json'):
    print(f"Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        raw_data = json.load(f)
        data = raw_data['data'] if 'data' in raw_data else raw_data
    
    # Configure publication quality settings
    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'serif',
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'legend.fontsize': 12,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight'
    })
    sns.set_style("whitegrid")
    
    output_dir = '../paper/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data
    n_values = sorted(list(set(entry['n'] for entry in data)))
    
    # ---------------------------------------------------------
    # Plot 1: Crossover Point / Scaling Analysis (Log Scale)
    # Tree Size vs n for Hard Instances (Subset-Sum)
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))
    
    target_type = 'subset_sum'
    type_data = [d for d in data if d['type'] == target_type]
    
    ns = np.array(n_values)
    
    avg_mitm = []
    avg_t_core = []
    avg_sqrt_tc = []
    
    for n_val in ns:
        n_subset = [d for d in type_data if d['n'] == n_val]
        avg_mitm.append(np.mean([d['mitm'] for d in n_subset]))
        avg_t_core.append(np.mean([d['T_core'] for d in n_subset]))
        avg_sqrt_tc.append(np.mean([d['sqrt_Tc'] for d in n_subset]))
        
    avg_mitm = np.array(avg_mitm)
    avg_t_core = np.array(avg_t_core)
    avg_sqrt_tc = np.array(avg_sqrt_tc)
    
    plt.plot(ns, avg_mitm, 'ro-', linewidth=2, label='Standard MitM ($2^{n/2}$)')
    plt.plot(ns, avg_t_core, 'ks-', linewidth=2, label='Classical B&B ($T_{LP}$)')
    plt.plot(ns, avg_sqrt_tc, 'bs-', linewidth=2, label='Quantum B&B ($\sqrt{T_{LP}}$)')
    
    # Add hypothetical crossover with poly(m) overhead
    # Let overhead = n^3
    quantum_overhead = avg_sqrt_tc * (ns**2.5) # Using 2.5 for visualization
    plt.plot(ns, quantum_overhead, 'g^--', linewidth=2, label='Quantum + Gate Overhead ($n^{2.5} \sqrt{T_{LP}}$)')
    
    plt.yscale('log')
    plt.xlabel('Number of Items ($n$)')
    plt.ylabel('Number of Operations (Log Scale)')
    plt.title('Asymptotic Scaling and Crossover Point (Subset-Sum)')
    plt.legend()
    
    plot1_path = os.path.join(output_dir, 'scaling_crossover.pdf')
    plt.savefig(plot1_path)
    plt.close()
    print(f"Saved {plot1_path}")
    
    # ---------------------------------------------------------
    # Plot 2: Synergy (Tree Size Reduction Bar Chart at n=24)
    # ---------------------------------------------------------
    n_target = max(n_values)
    n_data = [d for d in data if d['n'] == n_target]
    
    types_raw = list(set(d['type'] for d in n_data))
    types = []
    t_nolp = []
    t_core = []
    q_ops = []
    
    for t_raw in types_raw:
        types.append(t_raw.replace('-', '\n').title())
        t_subset = [d for d in n_data if d['type'] == t_raw]
        
        t_nolp.append(np.mean([d['mitm'] for d in t_subset]))
        t_core.append(np.mean([d['T_core'] for d in t_subset]))
        q_ops.append(np.mean([d['sqrt_Tc'] for d in t_subset]))
        
    x = np.arange(len(types))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width, t_nolp, width, label='No LP (MitM Baseline)', color='#E74C3C')
    rects2 = ax.bar(x, t_core, width, label='With LP (Classical)', color='#F39C12')
    rects3 = ax.bar(x + width, q_ops, width, label='With LP + Quantum', color='#3498DB')
    
    ax.set_ylabel('Number of Operations (Log Scale)')
    ax.set_title(f'Operation Reduction Pipeline ($n={n_target}$)')
    ax.set_xticks(x)
    ax.set_xticklabels(types)
    ax.set_yscale('log')
    ax.legend()
    
    fig.tight_layout()
    plot2_path = os.path.join(output_dir, 'tree_reduction.pdf')
    plt.savefig(plot2_path)
    plt.close()
    print(f"Saved {plot2_path}")

if __name__ == "__main__":
    generate_publication_plots()

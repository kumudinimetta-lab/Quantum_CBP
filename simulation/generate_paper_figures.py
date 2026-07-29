import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def generate_figures():
    output_dir = '../paper/figures'
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    # ---------------------------------------------------------
    # Figure 1: Large Scale Alpha Scaling
    # ---------------------------------------------------------
    try:
        with open('large_scale_alpha_raw.json', 'r') as f:
            alpha_data = json.load(f)
            
        ns = sorted(list(set(d['n'] for d in alpha_data)))
        uncorrelated_data = [d for d in alpha_data if d.get('class') == 'uncorrelated']
        
        plot_data = []
        for n in ns:
            alphas = [d['alpha'] for d in uncorrelated_data if d['n'] == n]
            if alphas:
                plot_data.append(alphas)
        
        if plot_data:
            plt.figure(figsize=(8, 6))
            plt.boxplot(plot_data, positions=ns, widths=max(1, ns[-1]/20))
            plt.plot(ns, [np.median(x) for x in plot_data], 'r--', label='Median Trend')
            plt.xscale('log')
            plt.xlabel('Number of Items ($n$)')
            plt.ylabel(r'Core Size Ratio ($\alpha = m/n$)')
            plt.title('LP Preprocessing Effectiveness (Uncorrelated)')
            plt.legend()
            plt.savefig(os.path.join(output_dir, 'alpha_scaling.pdf'))
            plt.close()
            print("Generated alpha_scaling.pdf")
    except Exception as e:
        print(f"Error generating alpha plot: {e}")

    # ---------------------------------------------------------
    # Figure 2: Spectral Validation Histogram
    # ---------------------------------------------------------
    try:
        with open('quantum_walk_spectral_full.json', 'r') as f:
            spectral_data = json.load(f)
            
        marked_p = []
        unmarked_p = []
        for run in spectral_data.get('records', []):
            if run.get('status') == 'COMPLETED':
                p_accept = run.get('p_accepts', {}).get('s0')
                if p_accept is not None:
                    if run.get('marked'):
                        marked_p.append(p_accept)
                    else:
                        unmarked_p.append(p_accept)
                        
        if marked_p and unmarked_p:
            plt.figure(figsize=(8, 6))
            plt.hist(marked_p, bins=30, alpha=0.7, label=f'Marked (N={len(marked_p)})', color='blue')
            plt.hist(unmarked_p, bins=30, alpha=0.7, label=f'Unmarked (N={len(unmarked_p)})', color='red')
            plt.axvline(0.5, color='black', linestyle='dashed', linewidth=2, label='Detection Threshold (0.5)')
            plt.xlabel('Phase Estimation Acceptance Probability ($p_{accept}$)')
            plt.ylabel('Frequency')
            plt.title('Distribution of $p_{accept}$ for Simulated Quantum Walks')
            plt.legend()
            plt.savefig(os.path.join(output_dir, 'spectral_histogram.pdf'))
            plt.close()
            print("Generated spectral_histogram.pdf")
    except Exception as e:
        print(f"Error generating spectral plot: {e}")

    # ---------------------------------------------------------
    # Figure 3: Hardware Results (IBM Fez)
    # ---------------------------------------------------------
    try:
        with open('ibm_hardware_results.json', 'r') as f:
            hw_data = json.load(f)
            
        ns_hw = [r['n'] for r in hw_data.get('instances', [])]
        sim_succ = [r['sim_success_prob'] for r in hw_data.get('instances', [])]
        hw_succ = [r['hw_success_prob'] for r in hw_data.get('instances', [])]
        
        x = np.arange(len(ns_hw))
        width = 0.35
        
        plt.figure(figsize=(8, 6))
        plt.bar(x - width/2, sim_succ, width, label='Ideal Simulator', color='royalblue')
        plt.bar(x + width/2, hw_succ, width, label='IBM Heron r2 (Hardware)', color='darkorange')
        
        random_guess = [1.0 / (2**n) for n in ns_hw]
        plt.plot(x, random_guess, 'k--', linewidth=2, label='Random Guessing (1/$2^m$)')
        
        plt.xlabel('Core Size ($m$)')
        plt.ylabel('Success Probability')
        plt.title('Amplitude Amplification on IBM Hardware')
        plt.xticks(x, [f'm={n}' for n in ns_hw])
        plt.legend()
        plt.savefig(os.path.join(output_dir, 'hardware_results.pdf'))
        plt.close()
        print("Generated hardware_results.pdf")
    except Exception as e:
        print(f"Error generating hardware plot: {e}")

if __name__ == "__main__":
    generate_figures()

"""Generate hardware validation plot for the paper."""
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'legend.fontsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Data from IBM Fez experiment
instances = [
    'Core-3A\n(Uncorr.)', 'Core-3B\n(Weak.)', 
    'Core-4A\n(Strong.)', 'Core-4B\n(Sub-sum)',
    'Core-5A\n(Uncorr.)', 'Core-5B\n(Weak.)',
    'Core-6A\n(Strong.)', 'Core-6B\n(Sub-sum)'
]
sim_probs  = [94.5, 94.5, 96.1, 96.1, 99.9, 96.1, 99.9, 99.8]
hw_probs   = [67.4, 66.7, 12.4, 13.4,  2.4,  6.4,  3.1,  3.3]
n_qubits   = [3, 3, 4, 4, 5, 5, 6, 6]
two_q_gates= [78, 72, 661, 659, 4017, 3012, 16579, 12456]

# Uniform baselines
uniform = [100.0 / (2**n) for n in n_qubits]

x = np.arange(len(instances))
width = 0.32

fig, ax1 = plt.subplots(figsize=(12, 6))

bars_sim = ax1.bar(x - width, sim_probs, width, label='Simulator (Ideal)', 
                    color='#2ecc71', alpha=0.85, edgecolor='#27ae60', linewidth=0.8)
bars_hw  = ax1.bar(x, hw_probs, width, label='IBM Fez (Hardware)', 
                    color='#3498db', alpha=0.85, edgecolor='#2980b9', linewidth=0.8)
bars_uni = ax1.bar(x + width, uniform, width, label='Uniform Baseline ($1/2^n$)',
                    color='#e74c3c', alpha=0.5, edgecolor='#c0392b', linewidth=0.8)

# Add NISQ boundary line
ax1.axvline(x=3.5, color='#e67e22', linestyle='--', linewidth=2, alpha=0.7)
ax1.text(3.7, 85, 'NISQ Noise\nBoundary', fontsize=11, color='#e67e22', 
         fontweight='bold', va='top')

# Labels on bars showing top-1 status
for i, (hw, n) in enumerate(zip(hw_probs, n_qubits)):
    label = 'Top-1' if i < 4 else 'Found'
    color = '#27ae60' if i < 4 else '#e74c3c'
    ax1.text(x[i], hw + 1.5, label, ha='center', va='bottom', fontsize=8, 
             color=color, fontweight='bold')

# n-qubit labels at bottom
for i, n in enumerate(n_qubits):
    ax1.text(x[i], -5, f'n={n}', ha='center', va='top', fontsize=10, 
             fontweight='bold', color='#2c3e50')

ax1.set_ylabel('Success Probability (%)')
ax1.set_title('Quantum Hardware Validation: Simulator vs. IBM Fez ($n=3$ to $n=6$)')
ax1.set_xticks(x)
ax1.set_xticklabels(instances, fontsize=9)
ax1.set_ylim(-8, 105)
ax1.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3)

# Secondary axis for 2Q gate count
ax2 = ax1.twinx()
ax2.plot(x, two_q_gates, 'k^--', linewidth=1.5, markersize=7, label='2Q Gate Count', alpha=0.6)
ax2.set_ylabel('Two-Qubit Gate Count', color='#555')
ax2.set_yscale('log')
ax2.tick_params(axis='y', labelcolor='#555')
ax2.legend(loc='center right')

fig.tight_layout()

output_dir = '../paper/figures'
os.makedirs(output_dir, exist_ok=True)
path = os.path.join(output_dir, 'hardware_validation.pdf')
plt.savefig(path)
plt.close()
print(f"Saved {path}")

# Also save PNG for preview
png_path = os.path.join(output_dir, 'hardware_validation.png')
fig2, ax1 = plt.subplots(figsize=(12, 6))
bars_sim = ax1.bar(x - width, sim_probs, width, label='Simulator (Ideal)', 
                    color='#2ecc71', alpha=0.85, edgecolor='#27ae60', linewidth=0.8)
bars_hw  = ax1.bar(x, hw_probs, width, label='IBM Fez (Hardware)', 
                    color='#3498db', alpha=0.85, edgecolor='#2980b9', linewidth=0.8)
bars_uni = ax1.bar(x + width, uniform, width, label='Uniform Baseline ($1/2^n$)',
                    color='#e74c3c', alpha=0.5, edgecolor='#c0392b', linewidth=0.8)
ax1.axvline(x=3.5, color='#e67e22', linestyle='--', linewidth=2, alpha=0.7)
ax1.text(3.7, 85, 'NISQ Noise\nBoundary', fontsize=11, color='#e67e22', fontweight='bold', va='top')
for i, (hw, n) in enumerate(zip(hw_probs, n_qubits)):
    label = 'Top-1' if i < 4 else 'Found'
    color = '#27ae60' if i < 4 else '#e74c3c'
    ax1.text(x[i], hw + 1.5, label, ha='center', va='bottom', fontsize=8, color=color, fontweight='bold')
ax1.set_ylabel('Success Probability (%)')
ax1.set_title('Quantum Hardware Validation: Simulator vs. IBM Fez ($n=3$ to $n=6$)')
ax1.set_xticks(x)
ax1.set_xticklabels(instances, fontsize=9)
ax1.set_ylim(-3, 105)
ax1.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3)
ax2 = ax1.twinx()
ax2.plot(x, two_q_gates, 'k^--', linewidth=1.5, markersize=7, label='2Q Gate Count', alpha=0.6)
ax2.set_ylabel('Two-Qubit Gate Count', color='#555')
ax2.set_yscale('log')
ax2.tick_params(axis='y', labelcolor='#555')
ax2.legend(loc='center right')
fig2.tight_layout()
plt.savefig(png_path, dpi=150)
plt.close()
print(f"Saved {png_path}")

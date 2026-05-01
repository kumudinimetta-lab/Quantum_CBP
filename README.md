# Hybrid Quantum-Classical Knapsack (HybridQuantumKnapsack)

This repository contains the implementation and research paper for a hybrid quantum-classical algorithm for the 0/1 Knapsack Problem. Our approach combines classical LP-based reduced-cost variable fixing with Montanaro's quantum branch-and-bound algorithm to achieve provable speedups on structured instances.

## Key Features
- **Phase 1: LP-Pruning**: Classical preprocessing to reduce problem size via reduced-cost variable fixing.
- **Phase 2: Quantum B&B**: Quantum walk-based search on the pruned branching tree.
- **Hardware Validation**: Empirical results on IBM Quantum (Fez/Heron) hardware identifying the NISQ noise boundary.
- **Large-Scale Evaluation**: Benchmarks on instances up to $n=10,000$ items.

## Repository Structure
- `/simulation`: Python implementation of the algorithm, benchmarks, and IBM Quantum execution scripts.
- `/paper`: IEEE-compliant LaTeX source for the research paper "LP-Pruned Quantum Branch-and-Bound for the 0/1 Knapsack Problem".
- `/references`: PDF copies of cited literature and research notes.

## Installation
```bash
pip install qiskit qiskit-ibm-runtime matplotlib numpy
```

## Authors
Developed as part of the Quantum Computing Research at Kumudini Metta Lab.

# Citations Verified

## (a) Reversible Addition (Draper QFT Adder)
- Status: VERIFIED
- Title: Addition on a Quantum Computer
- Authors: Thomas G. Draper
- Venue/Year: arXiv (quant-ph) / 2000
- Link: http://arxiv.org/abs/quant-ph/0008033
- What it provides: Provides a method for performing addition on a quantum computer using the Quantum Fourier Transform (QFT). It eliminates the need for temporary carry qubits (ancillae) used in classical ripple-carry adders.
- Reported resource cost (if any): For $n$-bit addition, it requires no ancillary qubits. It heavily relies on controlled-phase rotations.
- Note: This is exactly the "in-place Draper (QFT) arithmetic with zero ancilla" already utilized and cited for the predicate $V$ in the manuscript (Line 259). We can directly reuse this approach for $h$.

## (b) Reversible Multiplication (Vedral-Barenco-Ekert)
- Status: VERIFIED
- Title: Quantum Networks for Elementary Arithmetic Operations
- Authors: V. Vedral, A. Barenco, A. Ekert
- Venue/Year: Physical Review A / 1996 (Preprint 1995)
- Link: http://arxiv.org/abs/quant-ph/9511018
- What it provides: An explicit construction of quantum circuits for elementary arithmetic operations, specifically focusing on modular addition and multiplication which are critical for Shor's algorithm. It builds multiplication out of controlled addition networks.
- Reported resource cost (if any): The memory requirement (qubits) grows linearly with the size of the registers, operating entirely reversibly with explicitly detailed gate constructions.
- Note: A foundational, standard primary source for constructing reversible multiplication from simpler addition gates.

## (c) Reversible Division (Thapliyal Restoring Division)
- Status: VERIFIED
- Title: Quantum Circuit Design of Integer Division Optimizing Ancillary Qubits and T-Count
- Authors: Himanshu Thapliyal, T. S. S. Varun, Edgard Munoz-Coreas
- Venue/Year: arXiv / 2016
- Link: http://arxiv.org/abs/1609.01241
- What it provides: Implements the restoring division algorithm in a quantum circuit. It provides the building blocks for integer division by using controlled subtractors and conditionally restoring the remainder. 
- Reported resource cost (if any): Emphasizes minimizing T-count and T-depth, which are the dominant costs in fault-tolerant architectures (Clifford+T gate set).
- Note: Integer division can be adapted for fixed-point by carefully aligning the radix point. This satisfies the requirement for a real primary source on gate-level division avoiding floating-point heuristics.

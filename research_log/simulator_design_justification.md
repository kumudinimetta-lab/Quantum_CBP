# Gate-Level Simulator Design Justification

## 1. Explicit Confirmation of Gate-Level Execution
The simulator will execute the **ACTUAL gate sequence** from the synthesized `QuantumCircuit`. It will iterate through the unrolled `qc.data` (which will contain only fundamental gates: `x`, `cx`, `ccx`, `h`, `cp`, `swap`) in the exact order they appear. For each gate, it will apply the corresponding transformation to a localized state representation. It will **NOT** recompute "what the answer should be" via direct integer arithmetic. The exact purpose of this simulator is to detect wiring bugs, off-by-one errors, or improper uncomputations in the actual circuit construction, which the previous formula check could not do.

## 2. Representation of the Draper QFT Segment
For the Draper QFT segment, the simulator will track the state by maintaining a **Phase Angle Representation** for qubits in the Fourier domain, alongside the standard **Boolean Representation** for qubits in the computational basis.

- **Why it is exact:** The QFT-based adder relies on the mathematical property that applying the QFT to a classical computational basis state $|x\rangle$ produces an unentangled product state:
  $QFT|x\rangle = \bigotimes_{j=1}^n \frac{1}{\sqrt{2}} \left( |0\rangle + e^{2\pi i x / 2^j} |1\rangle \right)$
- Instead of maintaining a $2^n$ statevector, the simulator tracks the exact phase $\phi_j = (x / 2^j) \bmod 1$ for each qubit $j$. 
- When a controlled-phase rotation $CP(\theta)$ is applied from a classical control qubit (value $c \in \{0, 1\}$), the target qubit's phase is updated exactly: $\phi_j \leftarrow \phi_j + c \cdot \frac{\theta}{2\pi}$. 
- Because the target qubits never become entangled with each other or the control qubits (the controls remain strictly in the computational basis), the state remains completely separable at all times.
- When the inverse QFT is applied, if the phases correspond perfectly to the Fourier representation of an integer $z$, the state collapses back exactly to the classical computational basis state $|z\rangle$ with probability 1. This guarantees classical-basis-state-in implies classical-basis-state-out, allowing our simulator to perfectly and deterministically model the QFT segment without any approximations.

## 3. Simulator Integrity Verification (Unit Test)
To prove the simulator performs true gate-level verification, I will introduce a unit test that deliberately injects a wiring bug into the synthesized circuit before simulation.
- **Injected Bug:** E.g., swapping two control qubits on a `ccx` gate inside the Thapliyal divider, or altering a phase angle from $\pi/2$ to $\pi/4$ in the Draper adder.
- **Expected Outcome:** The simulator must deterministically process the faulty gate list, producing an incorrect boolean bitstring at the end, which triggers a mismatch when compared to the exact LP bound from `verification_against_exact_lp.py`.
- **Purpose:** If the simulator were bypassing the gates and re-evaluating the arithmetic directly, it would ignore the injected bug and falsely report success. Catching the bug proves the simulator is genuinely reading and executing the gate-level wiring.
